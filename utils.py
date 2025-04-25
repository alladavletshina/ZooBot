IMAGES_DIR = "./images/"

ANIMAL_IMAGES = {
    "Альпака": IMAGES_DIR + "alpaka.jpg",
    "Тигр": IMAGES_DIR + "tiger.jpg",
    "Волк": IMAGES_DIR + "wolf.jpg",
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
    }
]

score_to_animals = {
    range(2, 4): "Альпака",
    range(4, 6): "Тигр",
    range(6, 8): "Волк"
}

animal_descriptions = {
    "Альпака": "Верный друг, преданный и верный своим близким.",
    "Тигр": "Независимый дух, ценящий комфорт и уют.",
    "Волк": "Храбрый лидер, готовый защищать свою территорию."
}

ANIMAL_IMAGES = ""

def calculate_total_score(user_answers):
    total_points = sum([questions[i].get("points").get(ans, 0) for i, ans in enumerate(user_answers)])
    return total_points