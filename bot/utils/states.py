from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    admin_actions = State()


class UserState(StatesGroup):
    user_actions = State()