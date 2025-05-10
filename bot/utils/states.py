from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    admin_actions = State()
    ping_text = State()

    raffles_title = State()
    raffles_description = State()
    raffles_end_date = State()
    raffles_photo = State()
    raffles_requirements = State()

class RaffelChangeState(StatesGroup):
    raffel_action = State()
    raffel_change_description = State()
    raffel_change_photo = State()
    raffel_change_end_data = State()

class UserState(StatesGroup):
    user_actions = State()