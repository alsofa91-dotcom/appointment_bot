from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import date, timedelta


def main_menu():
    """
    Главное меню бота
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записаться", callback_data="book")]
    ])


def services_kb(services):
    """
    Кнопки выбора услуги
    services — список услуг из БД
    """
    keyboard = []

    for service_id, name, duration in services:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{name} ({duration} мин)",
                callback_data=f"service_{service_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def masters_kb(masters):
    """
    Кнопки выбора мастера
    """
    keyboard = []
    for master_id, name in masters:
        keyboard.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"master_{master_id}"
            )
        ])
    # кнопка отмены
    keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def dates_kb(days=7):
    """
    Кнопки выбора даты (сегодня + N дней)
    """
    keyboard = []
    today = date.today()

    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    for i in range(days):
        d = today + timedelta(days=i)
        if i == 0:
            text = f"Сегодня ({d.strftime('%d.%m')})"
        elif i == 1:
            text = f"Завтра ({d.strftime('%d.%m')})"
        else:
            text = f"{weekdays[d.weekday()]} ({d.strftime('%d.%m')})"

        keyboard.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"date_{d.isoformat()}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def times_kb(times):
    """
    Кнопки выбора времени
    times — список свободного времени
    """
    keyboard = []

    for t in times:
        keyboard.append([
            InlineKeyboardButton(
                text=t,
                callback_data=f"time_{t}"
            )
        ])

    # добавляем кнопку "Отмена" внизу
    keyboard.append([
        InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="confirm_no"),
        ]
    ])

