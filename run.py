from app.app import dp, bot

# Запуск основной части приложения
async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Остановлен вручную.")