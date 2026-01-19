from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from config import ADMIN_ID, WORKING_HOURS, DAYS_AHEAD
from database.db import (
    add_booking,
    get_services,
    get_masters,
    get_service_by_id,
    get_master_by_id,
    get_bookings_by_date
)
from keyboards.client_kb import (
    services_kb,
    masters_kb,
    dates_kb,
    times_kb,
    confirm_kb,
)
from states.booking_states import BookingStates

from datetime import date

router = Router()


# ---------------------------
# 1️⃣ Запись → выбор услуги
# ---------------------------
@router.callback_query(F.data == "book")
async def choose_service(callback: CallbackQuery, state: FSMContext):
    services = get_services()
    if not services:
        await callback.message.answer("❌ Услуги пока не добавлены")
        return

    await state.clear()
    await callback.message.answer(
        "Выберите услугу:",
        reply_markup=services_kb(services)
    )
    await state.set_state(BookingStates.service)
    await callback.answer()


# ---------------------------
# 2️⃣ Выбор услуги → мастер
# ---------------------------
@router.callback_query(BookingStates.service)
async def choose_master(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("service_"):
        return

    service_id = int(callback.data.replace("service_", ""))
    await state.update_data(service_id=service_id)

    masters = get_masters()
    if not masters:
        await callback.message.answer("❌ Мастера не добавлены")
        return

    await callback.message.answer(
        "Выберите мастера:",
        reply_markup=masters_kb(masters)
    )
    await state.set_state(BookingStates.master)
    await callback.answer()


# ---------------------------
# 3️⃣ Выбор мастера → дата
# ---------------------------
@router.callback_query(BookingStates.master)
async def choose_date(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("master_"):
        return

    master_id = int(callback.data.replace("master_", ""))
    await state.update_data(master_id=master_id)

    await callback.message.answer(
        "Выберите дату:",
        reply_markup=dates_kb(DAYS_AHEAD)
    )
    await state.set_state(BookingStates.date)
    await callback.answer()


# ---------------------------
# 4️⃣ Выбор даты → время
# ---------------------------
@router.callback_query(BookingStates.date)
async def choose_time(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("date_"):
        return

    selected_date = callback.data.replace("date_", "")
    await state.update_data(date=selected_date)

    # Получаем все занятые часы для выбранной даты
    busy_times = [t[0] for t in get_bookings_by_date(selected_date)]
    free_times = [t for t in WORKING_HOURS if t not in busy_times]

    if not free_times:
        await callback.message.answer("❌ Нет свободного времени")
        return

    await callback.message.answer(
        "Выберите время:",
        reply_markup=times_kb(free_times)
    )
    await state.set_state(BookingStates.time)
    await callback.answer()


# ---------------------------
# 5️⃣ ВЫБОР ВРЕМЕНИ → ПОДТВЕРЖДЕНИЕ
# ---------------------------
@router.callback_query(BookingStates.time)
async def confirm(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("time_"):
        return

    selected_time = callback.data.replace("time_", "")
    await state.update_data(time=selected_time)

    data = await state.get_data()
    service_name = get_service_by_id(data["service_id"])
    master_name = get_master_by_id(data["master_id"])

    await callback.message.answer(
        "Подтвердите запись:\n\n"
        f"🛠 Услуга: {service_name}\n"
        f"👨‍🔧 Мастер: {master_name}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}",
        reply_markup=confirm_kb()
    )
    await state.set_state(BookingStates.confirm)
    await callback.answer()


# ---------------------------
# 6️⃣ ПОДТВЕРЖДЕНИЕ → БД
# ---------------------------
@router.callback_query(BookingStates.confirm, F.data == "confirm_yes")
async def save_booking(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    service_name = get_service_by_id(data["service_id"])
    master_name = get_master_by_id(data["master_id"])

    # Сохраняем в БД
    add_booking(
        client_id=callback.from_user.id,
        client_name=callback.from_user.full_name,
        service_name=service_name,
        master_name=master_name,
        date=data["date"],
        time=data["time"]
    )

    # Сообщение клиенту
    await callback.message.answer(
        "✅ Вы успешно записаны!\n\n"
        f"🛠 Услуга: {service_name}\n"
        f"👨‍🔧 Мастер: {master_name}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}"
    )

    # 🔔 Уведомление админу
    await bot.send_message(
        ADMIN_ID,
        "📢 Новая запись!\n\n"
        f"🛠 Услуга: {service_name}\n"
        f"👨‍🔧 Мастер: {master_name}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n"
        f"👤 Пользователь: {callback.from_user.full_name} (ID: {callback.from_user.id})"
    )

    await state.clear()
    await callback.answer()


# ---------------------------
# 7️⃣ ОТМЕНА
# ---------------------------
@router.callback_query(BookingStates.confirm, F.data == "confirm_no")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Запись отменена")
    await callback.answer()
