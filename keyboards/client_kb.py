from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from datetime import datetime, timedelta


# ---------------------------
# Главное меню
# ---------------------------
def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Записаться", callback_data="book")]
        ]
    )


# ---------------------------
# Выбор услуги
# ---------------------------
def services_kb(services):
    keyboard = []

    for service_id, name, duration in services:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{name} ({duration} мин)",
                callback_data=f"service_{service_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------------
# Выбор мастера
# ---------------------------
def masters_kb(masters):
    keyboard = []

    for master_id, name in masters:
        keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"master_{master_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------------
# Выбор даты
# ---------------------------
def dates_kb(days_ahead: int):
    keyboard = []
    today = datetime.today()

    for i in range(days_ahead):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        label = date.strftime("%d.%m (%a)")

        keyboard.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"date_{date_str}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------------
# Выбор времени
# ---------------------------
def times_kb(times):
    keyboard = []

    for time in times:
        keyboard.append([
            InlineKeyboardButton(
                text=time,
                callback_data=f"time_{time}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ---------------------------
# Подтверждение записи
# ---------------------------
def confirm_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
                InlineKeyboardButton(text="❌ Отменить", callback_data="confirm_no")
            ]
        ]
    )


# ---------------------------
# Кнопка "Поделиться номером"
# ---------------------------
def phone_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📞 Поделиться номером телефона",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
