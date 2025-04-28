from config.config import API_TOKEN, ADMINS_IDS
from aiogram import Bot
from aiogram.types import Message

IMAGES_DIR = "images/"

ANIMAL_IMAGES = {
    "Альпака": IMAGES_DIR + "alpaka.jpg",
    "Тигр": IMAGES_DIR + "tiger.jpg",
    "Волк": IMAGES_DIR + "wolf.jpg",
    "Ленивец": IMAGES_DIR + "lazy_one.jpg",
    "Белый аист": IMAGES_DIR + "white_aist.jpg",
    "Неопределённое животное": IMAGES_DIR + "unknown.jpg"
}

questions = [
    {
        "text": "Какие места отдыха вам нравятся?",
        "options": ["Природа", "Городские парки", "Экстрим"],
        "points": {"Природа": 1, "Городские парки": 2, "Экстрим": 3}
    },
    {
        "text": "Что для вас важнее всего в отношениях?",
        "options": ["Эмоции", "Комфорт", "Безопасность"],
        "points": {"Эмоции": 1, "Комфорт": 2, "Безопасность": 3}
    },
    {
        "text": "Какой суперсилой вы хотели бы обладать?",
        "options": ["Телепортация", "Чтение мыслей", "Бессмертие"],
        "points": {"Телепортация": 2, "Чтение мыслей": 3, "Бессмертие": 1}
    },
    {
        "text": "Что бы вы выбрали на необитаемом острове?",
        "options": ["Нож", "Книгу", "Гамак"],
        "points": {"Нож": 3, "Книгу": 2, "Гамак": 1}
    },
    {
        "text": "Какой вы видите идеальную субботу?",
        "options": ["Активный отдых", "Творчество", "Ничегонеделание"],
        "points": {"Активный отдых": 3, "Творчество": 2, "Ничегонеделание": 1}
    }
]

# Переработанные диапазоны для 5 вопросов (макс. 15 баллов)
score_to_animals = {
    range(5, 8): "Альпака",      # 3 балла (было 2)
    range(8, 11): "Ленивец",     # 3 балла
    range(11, 13): "Белый аист", # 2 балла (новый буфер)
    range(13, 15): "Тигр",       # 2 балла (сузили)
    range(15, 16): "Волк"        # 1 балл (сильно ограничили)
}

animal_descriptions = {
    "Альпака": "Дружелюбный и общительный. Создаёт тёплую атмосферу вокруг себя.",
    "Ленивец": "Мудрый созерцатель. Ценит комфорт и гармонию в каждом моменте.",
    "Белый аист": "Целеустремлённый и дальновидный. Всегда видит общую картину.",
    "Тигр": "Решительный и независимый. Действует точно и эффективно.",
    "Волк": "Сильный лидер с развитым чувством ответственности за других.",
    "Неопределённое животное": "Уникальная личность, которую сложно классифицировать!"
}

def calculate_total_score(user_answers):
    total = sum(q["points"][a] for q, a in zip(questions, user_answers[:5]))  # Берем только 5 ответов
    # Мягкая корректировка крайних значений
    if total < 5: return min(total + 2, 5)  # Сдвигаем очень низкие баллы
    if total > 15: return max(total - 2, 15)  # Сдвигаем очень высокие баллы
    return total

async def delete_webhook():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook()
    await bot.session.close()

async def check_admin(message: Message):
    if message.from_user.id not in ADMINS_IDS:
        await message.answer("Доступ запрещён")
        return False
    return True
