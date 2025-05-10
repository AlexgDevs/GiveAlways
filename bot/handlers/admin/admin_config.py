from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    message,
    Message
)

from ...utils.states import AdminState, UserState
from ...keyboards.reply import (admin_main_menu,
                                user_menu_keyboard,
                                raffles_menu,
                                users_menu,
                                settings_menu,
                                stats_menu)

admin_router = Router()

ADMIN_IDS = [1169844663]

@admin_router.message(Command('admin'))
async def chek_admin(message: Message, state: FSMContext):

    user_id = message.from_user.id
    #check
    if user_id not in ADMIN_IDS:
        await message.answer('У вас нет прав для использования данной команды!')
        return
    
    await message.answer('Вы включили админ панель', reply_markup=admin_main_menu)
    await state.set_state(AdminState.admin_actions)


@admin_router.message(F.text=='⬅️ Главное меню', AdminState.admin_actions)
async def back_to_user_menu(message: Message, state: FSMContext):

    await message.answer('Вы вышли из админ меню', reply_markup=user_menu_keyboard)
    await state.set_state(UserState.user_actions)

@admin_router.message(F.text=='🎁 Розыгрыши', AdminState.admin_actions)
async def get_keyboard_raffiels(message: Message, state: FSMContext):

    await message.answer('Вы вошли в раздел розыгрыши', reply_markup=raffles_menu)

@admin_router.message(F.text=='👥 Пользователи', AdminState.admin_actions)
async def get_keyboard_users(message: Message, state: FSMContext):

    await message.answer('Вы вошли в раздел пользователи', reply_markup=users_menu)

@admin_router.message(F.text=='📊 Статистика', AdminState.admin_actions)
async def get_keyboard_static(message: Message, state: FSMContext):

    await message.answer('Вы вошли в раздел статистики', reply_markup=stats_menu)

@admin_router.message(F.text=='⚙️ Настройки', AdminState.admin_actions)
async def get_keyboard_static(message: Message, state: FSMContext):

    await message.answer('Вы вошли в раздел настройки', reply_markup=settings_menu)

@admin_router.message(F.text=='⬅️ Назад', AdminState.admin_actions)
async def get_back_menu(message: Message, state: FSMContext):

    await message.answer('Вы вернулись в главное меню', reply_markup=admin_main_menu)


@admin_router.message(F.text=='Отменить создание')
async def back_to_admin_menu(message: Message, state: FSMContext):
    
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return False

    else:
        await message.answer('Вы отменили создание', reply_markup=admin_main_menu)
        await state.clear()
        await state.set_state(AdminState.admin_actions)