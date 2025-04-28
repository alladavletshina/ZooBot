from aiogram import types
from aiogram.fsm.context import FSMContext

from app.states import QuizState
from services.database import Feedback, SessionLocal
import logging

async def enter_feedback(message: types.Message, state: FSMContext):
    cancel_button = types.InlineKeyboardButton(text="Отмена", callback_data="cancel_feedback")
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])
    await message.answer("Напишите ваш отзыв:", reply_markup=keyboard)
    await state.set_state(QuizState.leave_feedback)

async def cancel_feedback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отправка отзыва отменена")
    await state.clear()
    await callback.answer()

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