from aiogram import Router
from aiogram.types import Message

from keyboards.client_kb import main_menu

router = Router()


@router.message()
async def start_handler(message: Message):
    if message.text != "/start":
        return

    await message.answer(
        "Привет! 👋\n\n"
        "Я бот для записи на услуги.\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=main_menu()
    )