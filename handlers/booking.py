from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, WORKING_HOURS, DAYS_AHEAD

from database.models import (
    add_booking,
    get_services,
    get_masters,
    get_bookings_by_date,
    get_service_by_id,
    get_master_by_id
)

from keyboards.client_kb import (
    services_kb,
    masters_kb,
    dates_kb,
    times_kb,
    confirm_kb,
    phone_kb
)

from states.booking_states import BookingStates

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

    busy = get_bookings_by_date(selected_date)
    busy_times = [b[0] for b in busy]  # берем только время

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
# 5️⃣ ВЫБОР ВРЕМЕНИ → ЗАПРОС ТЕЛЕФОНА
# ---------------------------
@router.callback_query(BookingStates.time)
async def ask_phone(callback: CallbackQuery, state: FSMContext):
    if not callback.data.startswith("time_"):
        return

    selected_time = callback.data.replace("time_", "")
    await state.update_data(time=selected_time)

    await callback.message.answer(
        "📞 Для подтверждения записи, пожалуйста, поделитесь номером телефона:",
        reply_markup=phone_kb()
    )

    await state.set_state(BookingStates.phone)
    await callback.answer()

# ---------------------------
# 6️⃣ ПОЛУЧЕНИЕ ТЕЛЕФОНА → ПОДТВЕРЖДЕНИЕ
# ---------------------------
@router.message(BookingStates.phone, F.contact)
async def get_phone(message: Message, state: FSMContext):
    contact = message.contact

    # защита — номер должен принадлежать пользователю
    if contact.user_id != message.from_user.id:
        await message.answer("❌ Пожалуйста, отправьте СВОЙ номер телефона")
        return

    phone = contact.phone_number
    await state.update_data(phone=phone)

    data = await state.get_data()

    service_name = get_service_by_id(data["service_id"])
    master_name = get_master_by_id(data["master_id"])

    await message.answer(
        "Подтвердите запись:\n\n"
        f"🛠 Услуга: {service_name}\n"
        f"👨‍🔧 Мастер: {master_name}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n"
        f"📞 Телефон: {phone}",
        reply_markup=confirm_kb()
    )

    await state.set_state(BookingStates.confirm)

# ---------------------------
# 7️⃣ ПОДТВЕРЖДЕНИЕ → СОХРАНЕНИЕ
# ---------------------------
@router.callback_query(BookingStates.confirm, F.data == "confirm_yes")
async def save_booking(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    service_name = get_service_by_id(data["service_id"])
    master_name = get_master_by_id(data["master_id"])

    add_booking(
        client_id=callback.from_user.id,
        client_name=callback.from_user.full_name,
        service=service_name,
        master=master_name,
        date=data["date"],
        time=data["time"],
        phone=data["phone"]
    )

    # сообщение клиенту
    await callback.message.answer(
        "✅ Вы успешно записаны! Мы свяжемся с вами.",
        reply_markup=ReplyKeyboardRemove()
    )

    # ссылка на клиента
    username = callback.from_user.username
    user_link = (
        f"https://t.me/{username}"
        if username else
        f"tg://user?id={callback.from_user.id}"
    )

    # уведомление админу
    await bot.send_message(
        ADMIN_ID,
        "📢 Новая запись!\n\n"
        f"🛠 Услуга: {service_name}\n"
        f"👨‍🔧 Мастер: {master_name}\n"
        f"📅 Дата: {data['date']}\n"
        f"⏰ Время: {data['time']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"👤 Клиент: {user_link}"
    )

    await state.clear()
    await callback.answer()

# ---------------------------
# 8️⃣ ОТМЕНА
# ---------------------------
@router.callback_query(BookingStates.confirm, F.data == "confirm_no")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Запись отменена",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()
