# config.py
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

API_TOKEN = config.get('DEFAULT', 'API_TOKEN')
DB_USER = config.get('DEFAULT', 'DB_USER')
DB_PASSWORD = config.get('DEFAULT', 'DB_PASSWORD')
DB_HOST = config.get('DEFAULT', 'DB_HOST')
DB_PORT = config.get('DEFAULT', 'DB_PORT')
DB_NAME = config.get('DEFAULT', 'DB_NAME')
BOT_LINK = "t.me/ZooZoombot"
CONTACT_EMAIL = "atdavletshina@gmail.com"
CONTACT_PHONE = "+79150887621"
ZOO_WEBSITE = "https://moscowzoo.ru/about/guardianship"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
ADMINS_IDS=config.get('DEFAULT', 'ADMINS_IDS')