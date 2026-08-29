from os import getenv
from aiogram import Bot, Dispatcher
import asyncio
from dotenv import load_dotenv
from handlers.routes import router, check_reminders
from handlers.routes import init_db

load_dotenv()
dp = Dispatcher()
dp.include_router(router)
TOKEN = getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=TOKEN)
    await init_db()
    asyncio.create_task(check_reminders(bot))    
    print("Пішов запуск")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())