from aiogram import F, types
from aiogram.fsm.context import FSMContext
from bot_instance import dp, bot
from states import QuizState
from handlers.quiz_handlers import fill_quiz, process_answer
from handlers.feedback_handlers import enter_feedback, cancel_feedback, process_feedback
from handlers.support_handlers import contact_support, handle_contact_choice
from handlers import commands

# Включение роутеров
dp.include_router(commands.router)

# Регистрация обработчиков
dp.message(lambda msg: msg.text == "Запустить викторину 🔥")(fill_quiz)
dp.callback_query(QuizState.quiz_in_progress)(process_answer)

dp.message(lambda msg: msg.text == "Оставить отзыв ✏️")(enter_feedback)
dp.callback_query(F.data == "cancel_feedback", QuizState.leave_feedback)(cancel_feedback)
dp.message(QuizState.leave_feedback)(process_feedback)

dp.message(lambda msg: msg.text == "Связаться с поддержкой 💬")(contact_support)
dp.callback_query(QuizState.contact_support)(handle_contact_choice)

@dp.message(lambda msg: msg.text == "Закрыть ⛔")
async def close_app(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("До встречи! Приложение закрыто.", reply_markup=None)
