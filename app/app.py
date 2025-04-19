import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from config import API_TOKEN
from .database import Feedback, SessionLocal
from .utils import questions, animal_descriptions, score_to_animals, calculate_total_score

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Класс состояний для формы отзыва
class FeedbackForm(StatesGroup):
    waiting_for_feedback = State()

# Индекс текущего вопроса
current_question_index = 0
user_score = {}

# Стартовая команда `/start`
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    global current_question_index
    current_question_index = 0
    await ask_next_question(message.chat.id)

# Команда `/feedback` инициирует сбор отзыва
@dp.message(Command(commands=["feedback"]))
async def enter_feedback(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, напишите ваш отзыв ниже:")
    await state.set_state(FeedbackForm.waiting_for_feedback)

# Обработка отзыва пользователя
@dp.message(FeedbackForm.waiting_for_feedback)
async def process_feedback(message: types.Message, state: FSMContext):
    feedback_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username
    chat_id = message.chat.id

    # Создаем сессию для работы с базой данных
    db_session = SessionLocal()

    # Создаем новый объект Feedback и сохраняем отзыв
    new_feedback = Feedback(
        user_id=user_id,
        username=username,
        chat_id=chat_id,
        feedback_text=feedback_text
    )
    db_session.add(new_feedback)
    db_session.commit()

    await state.clear()
    await message.answer("Спасибо за ваш отзыв!")

    # Закрываем сессию
    db_session.close()

# Отправляем следующий вопрос
async def ask_next_question(chat_id):
    global current_question_index
    if current_question_index >= len(questions):
        final_result = determine_final_result()
        await bot.send_message(chat_id, f"Твой результат: {final_result}. {animal_descriptions.get(final_result)}")
        return

    question = questions[current_question_index]
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"{current_question_index}-{opt}")] for opt in question["options"]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await bot.send_message(chat_id, question["text"], reply_markup=keyboard)

# Определение итогового животного
def determine_final_result():
    total_points = calculate_total_score(list(user_score.values()))
    for score_range, animal in score_to_animals.items():
        if total_points in score_range:
            return animal
    return "Неопределённое животное"

# Обработка ответов пользователей
@dp.callback_query()
async def process_answer(callback_query: types.CallbackQuery):
    global current_question_index
    index, answer = map(str.strip, callback_query.data.split('-'))

    # Сохраняем ответ пользователя
    user_score[int(index)] = answer

    # Следующий вопрос
    current_question_index += 1
    await ask_next_question(callback_query.from_user.id)