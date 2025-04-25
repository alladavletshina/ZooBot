# config.py
API_TOKEN = "7702464166:AAHqwKv4dG6trelCc-xhkdVBorJrrSuJ6F8"

DB_USER = "postgres"
DB_PASSWORD = "911957"
DB_HOST = "localhost"  # Или IP-адрес сервера БД
DB_PORT = "5432"       # Стандартный порт PostgreSQL
DB_NAME = "zoobot"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"