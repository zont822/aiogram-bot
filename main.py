import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.routes import router, check_reminders, init_db


dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(token=BOT_TOKEN)
    await init_db()
    asyncio.create_task(check_reminders(bot))    
    print("Пішов запуск")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())