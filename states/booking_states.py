from aiogram.fsm.state import StatesGroup, State


class BookingStates(StatesGroup):
    service = State()   # выбор услуги
    master = State()    # выбор мастера
    date = State()      # выбор даты
    time = State()      # выбор времени
    phone = State()     # телефон
    confirm = State()   # подтверждение