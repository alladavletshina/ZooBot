from aiogram.fsm.state import State, StatesGroup

class QuizState(StatesGroup):
    quiz_in_progress = State()
    leave_feedback = State()
    contact_support = State()