import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from config import API_TOKEN, BOT_LINK, CONTACT_EMAIL, CONTACT_PHONE, ZOO_WEBSITE
from database import Feedback, SessionLocal
from utils import questions, animal_descriptions, score_to_animals, calculate_total_score

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class QuizState(StatesGroup):
    quiz_in_progress = State()
    leave_feedback = State()
    contact_support = State()

current_question_index = 0
user_score = {}

# Словарь с соответствием животных и путей к их изображениям
ANIMAL_IMAGES = {
    "Собака": "./images/alpaka.jpg",
    "Тигр": "./images/tiger.jpg",
    "Волк": "./images/wolf.jpg",
    "Неопределённое животное": "./images/unknown.jpg"
}

# Главное меню
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Запустить викторину 🔥")],
    [KeyboardButton(text="Оставить отзыв ✏️")],
    [KeyboardButton(text="Связаться с поддержкой 💬")],
    [KeyboardButton(text="Закрыть ⛔")]
], resize_keyboard=True)

# Кнопка для публикации результата
share_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✨ Поделиться моим результатом", switch_inline_query=f"Моя викторина: {BOT_LINK}")]
])

contact_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Написать письмо", callback_data="send_email")],
    [InlineKeyboardButton(text="Позвонить", callback_data="make_call")]
])

opportunity_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Узнать больше о Клубе друзей", url=ZOO_WEBSITE)]
])

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Добро пожаловать в наше приложение!\n\nГлавное меню:", reply_markup=main_menu)

@dp.message(lambda msg: msg.text == "Запустить викторину 🔥")
async def fill_quiz(message: types.Message, state: FSMContext):
    global current_question_index
    current_question_index = 0
    await ask_next_question(message.chat.id, state)
    await state.set_state(QuizState.quiz_in_progress)

from aiogram.types.input_file import FSInputFile  # Импортируем класс FSInputFile

async def ask_next_question(chat_id, state: FSMContext):
    global current_question_index
    if current_question_index >= len(questions):
        final_result = determine_final_result()
        result_message = f"Поздравляю! Твоё животное — {final_result}!\n\n{animal_descriptions.get(final_result)}.\n\n"
        result_message += "🐾 Ты можешь поддержать нашего друга, став членом Клуба друзей зоопарка. Каждая твоя копейка помогает сохранить природу и разнообразие нашей планеты.\n\n"
        result_message += "Присоединяйся к нашим друзьям и сделай мир немного добрее!"

        # Получаем путь к изображению животного
        image_path = ANIMAL_IMAGES.get(final_result, ANIMAL_IMAGES['Неопределённое животное'])

        # Отправляем изображение с подписью, используя FSInputFile
        await bot.send_photo(chat_id, FSInputFile(image_path), caption=result_message)

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

@dp.message(lambda msg: msg.text == "Оставить отзыв ✏️")
async def enter_feedback(message: types.Message, state: FSMContext):
    cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel_feedback")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])
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

@dp.message(lambda msg: msg.text == "Связаться с поддержкой 💬")
async def contact_support(message: types.Message, state: FSMContext):
    await message.answer("Выберите удобный способ связи:", reply_markup=contact_button)
    await state.set_state(QuizState.contact_support)

@dp.callback_query(QuizState.contact_support)
async def handle_contact_choice(callback_query: types.CallbackQuery, state: FSMContext):
    method = callback_query.data
    final_result = determine_final_result()
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username or "аноним"

    match method:
        case "send_email":
            email_subject = f"[Викторина]: Вопрос от {username} ({user_id})"
            email_body = (
                f"Пользователь: {username}\n"
                f"ID пользователя: {user_id}\n"
                f"Результат викторины: {final_result}\n"
                "\n"
                "Ваш вопрос или предложение?"
            )
            await bot.send_message(callback_query.from_user.id, f"Отправьте своё сообщение нам на почту: {CONTACT_EMAIL}.\nТема письма: '{email_subject}'")
        case "make_call":
            phone_number = CONTACT_PHONE
            await bot.send_message(callback_query.from_user.id, f"Позвоните нам по номеру: {phone_number}")

    await state.clear()
    await callback_query.answer()

@dp.message(lambda msg: msg.text == "Закрыть ⛔")
async def close_app(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("До встречи! Приложение закрыто.", reply_markup=None)

def determine_final_result():
    total_points = calculate_total_score(list(user_score.values()))
    for score_range, animal in score_to_animals.items():
        if total_points in score_range:
            return animal
    return "Неопределённый результат"