from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    message,
    Message
)

from ...utils.states import AdminState
from ...keyboards.reply import admin_menu_keyboard

admin_router = Router()

ADMIN_IDS = [1169844663]

@admin_router.message(Command('admin'))
async def chek_admin(message: Message, state: FSMContext):

    user_id = message.from_user.id
    #check
    if user_id not in ADMIN_IDS:
        await message.answer('У вас нет прав для использования данной команды!')
        return
    
    await message.answer('Вы включили админ панель', reply_markup=admin_menu_keyboard)
    await state.set_state(AdminState.admin_actions)