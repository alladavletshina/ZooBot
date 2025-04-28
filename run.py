from app.app import dp, bot
from utils.utils import delete_webhook
import asyncio

async def main():
    await dp.start_polling(bot)
    asyncio.run(delete_webhook())

if __name__ == "__main__":
    asyncio.run(main())
