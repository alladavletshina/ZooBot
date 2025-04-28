from aiogram import types
from aiogram.fsm.context import FSMContext

from app.bot_instance import bot
from app.keyboards import contact_button
from app.states import QuizState
from config.config import CONTACT_EMAIL, CONTACT_PHONE
from handlers.quiz_handlers import determine_final_result

async def contact_support(message: types.Message, state: FSMContext):
    await message.answer("Выберите удобный способ связи:", reply_markup=contact_button)
    await state.set_state(QuizState.contact_support)

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