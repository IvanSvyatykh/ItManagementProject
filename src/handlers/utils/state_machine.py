from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    phone_number = State()
    waiting_for_period = State()
    # Для понимания надо обновлять сообщение, или удалять предыдущее
    from_refresh = State()


class BookingStates(StatesGroup):
    CONFIRM_DATE = State()
    SELECT_DATE = State()
    INPUT_TIME = State()
    CONFIRM_BOOKING = State()
    INPUT_SUMMARY = State()
    INPUT_DESCRIPTION = State()
