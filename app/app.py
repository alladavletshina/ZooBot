import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.command import CommandStart
from config import API_TOKEN
from .utils import questions, animal_descriptions, score_to_animals, calculate_total_score

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Индекс текущего вопроса
current_question_index = 0
user_score = {}

# Стартовая команда `/start`
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    global current_question_index
    current_question_index = 0
    await ask_next_question(message.chat.id)


# Отправляем следующий вопрос
async def ask_next_question(chat_id):
    global current_question_index
    if current_question_index >= len(questions):
        final_result = determine_final_result()
        await bot.send_message(chat_id, f"Твой результат: {final_result}. {animal_descriptions.get(final_result)}")
        return

    question = questions[current_question_index]
    buttons = [[InlineKeyboardButton(text=opt, callback_data=f"{current_question_index}-{opt}")] for opt in
               question["options"]]
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

    # Сохранение ответа пользователя
    user_score[int(index)] = answer

    # Следующий вопрос
    current_question_index += 1
    await ask_next_question(callback_query.from_user.id)