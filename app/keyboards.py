from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.config import ZOO_WEBSITE, BOT_LINK

# Главное меню
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Запустить викторину 🔥")],
    [KeyboardButton(text="Оставить отзыв ✏️")],
    [KeyboardButton(text="Связаться с поддержкой 💬")],
    [KeyboardButton(text="Клуб друзей 🐾")],
    [KeyboardButton(text="Закрыть ⛔")]
], resize_keyboard=True)

contact_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Написать письмо", callback_data="send_email")],
    [InlineKeyboardButton(text="Позвонить", callback_data="make_call")]
])

opportunity_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Узнать больше о Клубе друзей", url=ZOO_WEBSITE)]
])

async def create_share_keyboard(result: str):
    builder = InlineKeyboardBuilder()
    share_text = (
        f"Я прошёл викторину и мой результат - {result}! "
        f"А какое твоё тотемное животное? Пройди тест: {BOT_LINK}"
    )

    builder.row(
        InlineKeyboardButton(
            text="📢 Поделиться в Telegram",
            url=f"https://t.me/share/url?url={BOT_LINK}&text={share_text}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🌍 Поделиться в других сетях",
            callback_data=f"share_ext_{result}"
        )
    )
    return builder.as_markup()