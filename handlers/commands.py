from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from app.keyboards import main_menu, opportunity_button  # Импортируем из keyboards.py

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Добро пожаловать в наше приложение!\n\n"
        "Здесь вы можете:\n"
        "- Пройти викторину и узнать свое тотемное животное\n"
        "- Присоединиться к Клубу друзей зоопарка\n"
        "- Оставить отзыв или связаться с поддержкой\n\n"
        "Выберите действие:",
        reply_markup=main_menu
    )

@router.message(F.text == "Клуб друзей 🐾")
async def friends_club_info(message: types.Message):
    await message.answer(
        "🐯 Клуб друзей зоопарка 🦁\n\n"
        "Присоединяйтесь к нашему сообществу и поддерживайте животных!\n"
        "Ваше участие помогает:\n"
        "- Сохранять редкие виды\n"
        "- Создавать комфортные условия для животных\n"
        "- Развивать образовательные программы\n\n"
        "Каждый член клуба получает:\n"
        "✅ Эксклюзивные новости\n"
        "✅ Возможность посещать закрытые мероприятия\n"
        "✅ Именной сертификат",
        reply_markup=opportunity_button  # Теперь берем из keyboards
    )