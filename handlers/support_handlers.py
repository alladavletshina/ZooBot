from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold, hlink, hitalic
from urllib.parse import quote

from app.keyboards import contact_button
from app.states import QuizState
from config.config import CONTACT_PHONE, CONTACT_EMAIL
from handlers.quiz_handlers import determine_final_result


async def contact_support(message: types.Message, state: FSMContext) -> None:

    await message.answer(
        "✨ <b>Выберите способ связи:</b> ✨",
        reply_markup=contact_button,
        parse_mode="HTML"
    )
    await state.set_state(QuizState.contact_support)


async def handle_contact_choice(callback_query: types.CallbackQuery, state: FSMContext) -> None:

    contact_method = callback_query.data
    final_result = determine_final_result() or "не определён"
    user = callback_query.from_user
    username = user.username or "анонимный пользователь"
    first_name = user.first_name or ""


    user_info = (
        f"\n👤 {hbold(f'{first_name}') if first_name else ''}"
        f"\n🔹 {hitalic(f'@{username}') if username.startswith('@') else hitalic(username)}"
        f"\n🆔 ID: {user.id}"
        f"\n🏆 Результат: {hbold(final_result)}"
    )

    match contact_method:
        case "send_email":
            email_subject = quote(f"Вопрос по викторине от {first_name or username}")
            await callback_query.message.answer(
                f"📮 {hbold('Электронная почта:')}\n"
                f"└ {hlink(CONTACT_EMAIL, f'mailto:{CONTACT_EMAIL}?subject={email_subject}')}\n\n"
                f"📝 {hbold('Рекомендуемая тема:')}\n"
                f"└ «Вопрос по викторине от {first_name or username}»\n"
                f"{user_info}\n\n"
                f"💌 {hitalic('Опишите ваш вопрос подробнее, и мы ответим в течение 24 часов')}",
                parse_mode="HTML",
                disable_web_page_preview=True
            )

        case "make_call":
            await callback_query.message.answer(
                f"📱 {hbold('Телефон для связи:')}\n"
                f"└ {hlink(CONTACT_PHONE, f'tel:{CONTACT_PHONE}')}\n\n"
                f"🕒 {hbold('Часы работы:')}\n"
                f"└ Пн-Пт: 9:00-18:00\n"
                f"└ Сб-Вс: выходной\n"
                f"{user_info}\n\n"
                f"☎️ {hitalic('Для быстрого решения вопроса рекомендуем звонок')}",
                parse_mode="HTML",
                disable_web_page_preview=True
            )

        case _:
            await callback_query.message.answer(
                "⚠️ Извините, этот способ связи временно недоступен\n"
                "Попробуйте выбрать другой вариант",
                parse_mode="HTML"
            )

    await state.clear()
    await callback_query.answer()