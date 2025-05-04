from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    admin_actions = State()

    raffles_title = State()
    raffles_description = State()
    raffles_end_date = State()
    raffles_photo = State()

class UserState(StatesGroup):
    user_actions = State()