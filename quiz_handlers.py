from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types.input_file import FSInputFile

from bot_instance import bot, dp
from config.config import BOT_LINK
from states import QuizState
from keyboards import create_share_keyboard
from utils import questions, ANIMAL_IMAGES, animal_descriptions, calculate_total_score, score_to_animals

current_question_index = 0
user_score = {}

async def ask_next_question(chat_id: int, state: FSMContext):
    global current_question_index
    if current_question_index >= len(questions):
        final_result = determine_final_result()
        await send_quiz_result(chat_id, final_result)
        await state.clear()
        return

    question = questions[current_question_index]
    buttons = [[types.InlineKeyboardButton(text=opt, callback_data=f"{current_question_index}-{opt}")]
               for opt in question["options"]]
    await bot.send_message(
        chat_id,
        question["text"],
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons)
    )

async def send_quiz_result(chat_id: int, result: str):
    image_path = ANIMAL_IMAGES.get(result, ANIMAL_IMAGES['Неопределённое животное'])
    caption = (
        f"🎉 <b>Ваш результат:</b> {result}!\n\n"
        f"{animal_descriptions[result]}\n\n"
        f"Поделитесь результатом с друзьями!\n"
        f"<i>Пройти викторину:</i> {BOT_LINK}"
    )

    await bot.send_photo(
        chat_id,
        photo=FSInputFile(image_path),
        caption=caption,
        reply_markup=await create_share_keyboard(result),
        parse_mode="HTML"
    )

@dp.callback_query(F.data.startswith("share_ext_"))
async def share_external(callback: types.CallbackQuery):
    animal = callback.data.split('_')[2]
    await callback.answer()
    await bot.send_message(
        callback.from_user.id,
        f"Скопируйте это сообщение для публикации:\n\n"
        f"Моё тотемное животное - {animal}!\n\n"
        f"Хочешь узнать своё? Пройди викторину:\n{BOT_LINK}"
    )

def determine_final_result():
    total_points = calculate_total_score(list(user_score.values()))
    for score_range, animal in score_to_animals.items():
        if total_points in score_range:
            return animal
    return "Неопределённый результат"

async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    global current_question_index
    index, answer = callback.data.split('-')
    user_score[int(index)] = answer
    current_question_index += 1
    await ask_next_question(callback.from_user.id, state)
    await callback.answer()

async def fill_quiz(message: types.Message, state: FSMContext):
    global current_question_index
    current_question_index = 0
    await ask_next_question(message.chat.id, state)
    await state.set_state(QuizState.quiz_in_progress)