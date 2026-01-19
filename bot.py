import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.admin import router as admin_router
from handlers.start import router as start_router
from handlers.booking import router as booking_router
from database.db import init_db


async def main():
    init_db()  # ← здесь правильнее

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # порядок нормальный
    dp.include_router(admin_router)
    dp.include_router(start_router)
    dp.include_router(booking_router)

    print("Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
