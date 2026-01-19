from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_ID
from database.db import (
    add_service,
    get_services,
    update_service,
    delete_service,
    add_master,
    get_masters,
    update_master,
    delete_master,
    get_service_by_id,
    get_master_by_id,
    get_all_bookings,
    get_bookings_by_date,
    get_bookings_between
)
from datetime import date, timedelta

router = Router()


# ---------------------------
# FSM состояния для админки
# ---------------------------
class AdminStates(StatesGroup):
    waiting_name = State()
    waiting_duration = State()
    waiting_master_name = State()
    waiting_edit_service_id = State()
    waiting_edit_service_name = State()
    waiting_edit_service_duration = State()
    waiting_edit_master_id = State()
    waiting_edit_master_name = State()
    waiting_delete_service_id = State()
    waiting_delete_master_id = State()


# ---------------------------
# Проверка админа
# ---------------------------
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ---------------------------
# /admin — старт админки
# ---------------------------
@router.message(F.text.regexp(r"^/admin(@\w+)?$"))
async def admin_start(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа.")
        return
    await message.answer(
        "👨‍💼 Добро пожаловать в админку!\n"
        "Команды:\n"
        "1. Добавить услугу — /add_service\n"
        "2. Посмотреть услуги — /list_services\n"
        "3. Редактировать услугу — /edit_service\n"
        "4. Удалить услугу — /delete_service\n"
        "5. Добавить мастера — /add_master\n"
        "6. Посмотреть мастеров — /masters\n"
        "7. Редактировать мастера — /edit_master\n"
        "8. Удалить мастера — /delete_master\n"
        "9. Просмотр всех записей — /bookings\n"
        "10. Записи на сегодня — /today\n"
        "11. Записи на неделю — /week"
    )


# ---------------------------
# Добавление услуги
# ---------------------------
@router.message(F.text.regexp(r"^/add_service(@\w+)?$"))
async def add_service_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Введите название услуги:")
    await state.set_state(AdminStates.waiting_name)

@router.message(AdminStates.waiting_name)
async def add_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите длительность услуги в минутах (число):")
    await state.set_state(AdminStates.waiting_duration)

@router.message(AdminStates.waiting_duration)
async def add_service_duration(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число минут.")
        return
    add_service(name=data["name"], duration=duration)
    await message.answer(f"✅ Услуга '{data['name']}' ({duration} мин) добавлена.")
    await state.clear()


# ---------------------------
# Список услуг
# ---------------------------
@router.message(F.text.regexp(r"^/list_services(@\w+)?$"))
async def list_services(message: Message):
    if not is_admin(message.from_user.id):
        return
    services = get_services()
    if not services:
        await message.answer("Услуги пока не добавлены.")
        return
    text = "Список услуг:\n"
    for s in services:
        text += f"{s[0]}. {s[1]} — {s[2]} мин\n"
    await message.answer(text)


# ---------------------------
# Добавление мастера
# ---------------------------
@router.message(F.text.regexp(r"^/add_master(@\w+)?$"))
async def add_master_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Введите имя мастера:")
    await state.set_state(AdminStates.waiting_master_name)

@router.message(AdminStates.
waiting_master_name)
async def add_master_name(message: Message, state: FSMContext):
    add_master(name=message.text)
    await message.answer(f"✅ Мастер '{message.text}' добавлен.")
    await state.clear()


# ---------------------------
# Список мастеров
# ---------------------------
@router.message(F.text.regexp(r"^/masters(@\w+)?$"))
async def list_masters(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа.")
        return
    masters = get_masters()
    if not masters:
        await message.answer("Мастера пока не добавлены.")
        return
    text = "Список мастеров:\n"
    for m_id, name in masters:
        text += f"{m_id}. {name}\n"
    await message.answer(text)


# ---------------------------
# Редактирование услуги
# ---------------------------
@router.message(F.text.regexp(r"^/edit_service(@\w+)?$"))
async def edit_service_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    services = get_services()
    if not services:
        await message.answer("Услуги пока не добавлены.")
        return
    text = "Выберите ID услуги для редактирования:\n"
    for s in services:
        text += f"{s[0]}. {s[1]} — {s[2]} мин\n"
    await message.answer(text)
    await state.set_state(AdminStates.waiting_edit_service_id)

@router.message(AdminStates.waiting_edit_service_id)
async def edit_service_choose(message: Message, state: FSMContext):
    try:
        service_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число ID.")
        return
    await state.update_data(service_id=service_id)
    await message.answer("Введите новое название услуги:")
    await state.set_state(AdminStates.waiting_edit_service_name)

@router.message(AdminStates.waiting_edit_service_name)
async def edit_service_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите новую длительность услуги в минутах:")
    await state.set_state(AdminStates.waiting_edit_service_duration)

@router.message(AdminStates.waiting_edit_service_duration)
async def edit_service_duration(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число минут.")
        return
    update_service(service_id=data["service_id"], name=data["name"], duration=duration)
    await message.answer(f"✅ Услуга '{data['name']}' обновлена ({duration} мин).")
    await state.clear()


# ---------------------------
# Удаление услуги
# ---------------------------
@router.message(F.text.regexp(r"^/delete_service(@\w+)?$"))
async def delete_service_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    services = get_services()
    if not services:
        await message.answer("Услуги пока не добавлены.")
        return
    text = "Выберите ID услуги для удаления:\n"
    for s in services:
        text += f"{s[0]}. {s[1]} — {s[2]} мин\n"
    await message.answer(text)
    await state.set_state(AdminStates.waiting_delete_service_id)

@router.message(AdminStates.waiting_delete_service_id)
async def delete_service_confirm(message: Message, state: FSMContext):
    try:
        service_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число ID.")
        return
    delete_service(service_id)
    await message.answer("✅ Услуга удалена.")
    await state.clear()


# ---------------------------
# Редактирование мастера
# ---------------------------
@router.message(F.text.regexp(r"^/edit_master(@\w+)?$"))
async def edit_master_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    masters = get_masters()
    if not masters:
        await message.answer("Мастера пока не добавлены.")
        return
    text = "Выберите ID мастера для редактирования:\n"
    for m_id, name in masters:
        text += f"{m_id}. {name}\n"
    await message.answer(text)
    await state.set_state(AdminStates.waiting_edit_master_id)

@router.message(AdminStates.waiting_edit_master_id)
async def edit_master_choose(message: Message, state: FSMContext):
    try:
        master_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число ID.")
        return
    await state.update_data(master_id=master_id)
    await message.answer("Введите новое имя мастера:")
    await state.set_state(AdminStates.waiting_edit_master_name)

@router.message(AdminStates.waiting_edit_master_name)
async def edit_master_name(message: Message, state: FSMContext):
    data = await state.get_data()
    update_master(master_id=data["master_id"], name=message.text)
    await message.answer(f"✅ Мастер обновлён: {message.text}")
    await state.clear()


# ---------------------------
# Удаление мастера
# ---------------------------
@router.message(F.text.regexp(r"^/delete_master(@\w+)?$"))
async def delete_master_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    masters = get_masters()
    if not masters:
        await message.answer("Мастера пока не добавлены.")
        return
    text = "Выберите ID мастера для удаления:\n"
    for m_id, name in masters:
        text += f"{m_id}. {name}\n"
    await message.answer(text)
    await state.set_state(AdminStates.waiting_delete_master_id)

@router.message(AdminStates.waiting_delete_master_id)
async def delete_master_confirm(message: Message, state: FSMContext):
    try:
        master_id = int(message.text)
    except ValueError:
        await message.answer("❌ Введите число ID.")
        return
    delete_master(master_id)
    await message.answer("✅ Мастер удалён.")
    await state.clear()


# ---------------------------
# Просмотр всех записей
# ---------------------------
@router.message(F.text.regexp(r"^/bookings(@\w+)?$"))
async def list_bookings(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа.")
        return

    bookings = get_all_bookings()
    
    if not bookings:
        await message.answer("Записей пока нет.")
        return

    text = "📋 Все записи:\n\n"
    for b_id, user_id, service_name, master_name, date_str, time_str in bookings:
        text += (
            f"ID: {b_id}\n"
            f"Пользователь: {user_id}\n"
            f"Услуга: {service_name}\n"
            f"Мастер: {master_name}\n"
            f"Дата: {date_str}\n"
            f"Время: {time_str}\n"
            "--------------------\n"
        )
    await message.answer(text)


# ---------------------------
# /today — записи на сегодня
# ---------------------------
@router.message(F.text.regexp(r"^/today(@\w+)?$"))
async def cmd_today(message: Message):
    if not is_admin(message.from_user.id):
        return

    today_date = date.today().isoformat()
    bookings = get_bookings_by_date(today_date)

    if not bookings:
        await message.answer("📅 На сегодня записей нет")
        return

    text = "📅 <b>Записи на сегодня:</b>\n\n"
    for time_, service, master, client in bookings:
        text += f"⏰ {time_} — {service} — {master} ({client})\n"

    await message.answer(text, parse_mode="HTML")


# ---------------------------
# /week — записи на ближайшие 7 дней
# ---------------------------
@router.message(F.text.regexp(r"^/week(@\w+)?$"))
async def cmd_week(message: Message):
    if not is_admin(message.from_user.id):
        return

    start_date = date.today()
    end_date = start_date + timedelta(days=7)

    rows = get_bookings_between(start_date.isoformat(), end_date.isoformat())

    if not rows:
        await message.answer("📆 На ближайшую неделю записей нет")
        return

    text = "📆 <b>Записи на неделю:</b>\n\n"
    current_date = None

    for booking_date, time_, service, master, client in rows:
        if booking_date != current_date:
            text += f"\n<b>{booking_date}</b>\n"
            current_date = booking_date
        text += f"⏰ {time_} — {service} — {master} ({client})\n"

    await message.answer(text, parse_mode="HTML")
