import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from config import API_TOKEN
from database import Feedback, SessionLocal
from utils import questions, animal_descriptions, score_to_animals, calculate_total_score

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class QuizState(StatesGroup):
    quiz_in_progress = State()
    leave_feedback = State()

current_question_index = 0
user_score = {}

# Основное меню
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Заполнить квиз")],
    [KeyboardButton(text="Оставить отзыв")]
], resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в наше приложение!\n\nГлавное меню:", reply_markup=main_menu)

@dp.message(lambda msg: msg.text == "Заполнить квиз")
async def fill_quiz(message: types.Message, state: FSMContext):
    global current_question_index
    current_question_index = 0
    await ask_next_question(message.chat.id, state)
    await state.set_state(QuizState.quiz_in_progress)

async def ask_next_question(chat_id, state: FSMContext):
    global current_question_index
    if current_question_index >= len(questions):
        final_result = determine_final_result()
        result_message = f"Твой результат: {final_result}. {animal_descriptions.get(final_result)}"
        await bot.send_message(chat_id, result_message)
        await state.clear()
        return

    question = questions[current_question_index]
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"{current_question_index}-{opt}")] for opt in question["options"]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id, question["text"], reply_markup=keyboard)

@dp.callback_query(QuizState.quiz_in_progress)
async def process_answer(callback_query: types.CallbackQuery, state: FSMContext):
    global current_question_index
    index, answer = map(str.strip, callback_query.data.split('-'))
    user_score[int(index)] = answer
    current_question_index += 1
    await ask_next_question(callback_query.from_user.id, state)
    await callback_query.answer()

@dp.message(lambda msg: msg.text == "Оставить отзыв")
async def enter_feedback(message: types.Message, state: FSMContext):
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel_feedback")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])  # Исправлено тут
    await message.answer("Напишите ваш отзыв:", reply_markup=keyboard)
    await state.set_state(QuizState.leave_feedback)

@dp.callback_query(F.data == "cancel_feedback", QuizState.leave_feedback)
async def cancel_feedback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отправка отзыва отменена")
    await state.clear()
    await callback.answer()

@dp.message(QuizState.leave_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    db_session = SessionLocal()
    try:
        new_feedback = Feedback(
            user_id=user_id,
            username=username,
            chat_id=chat_id,
            feedback_text=feedback_text
        )
        db_session.add(new_feedback)
        db_session.commit()
        await message.answer("Спасибо за ваш отзыв!")
    except Exception as e:
        logging.error(f"Ошибка при сохранении отзыва: {e}")
        await message.answer("Произошла ошибка при сохранении отзыва")
    finally:
        db_session.close()
        await state.clear()

def determine_final_result():
    total_points = calculate_total_score(list(user_score.values()))
    for score_range, animal in score_to_animals.items():
        if total_points in score_range:
            return animal
    return "Неопределённое животное"