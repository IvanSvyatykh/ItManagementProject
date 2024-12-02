from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    phone_number = State()
    waiting_for_period = State()
