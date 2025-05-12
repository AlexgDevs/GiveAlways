import asyncio

from sqlalchemy import select
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.types import (
    message,
    Message,
    ReplyKeyboardRemove,
    callback_query,
    CallbackQuery,
    ChatPermissions
)

from ..user.active_raffles import get_channel_id
from ...keyboards.reply import admin_main_menu
from ...keyboards.inline import condition_buttons
from ...database import (Session,
                        User,
                        Giveaway)


from ...utils.states import AdminState



work_with_user = Router()



@work_with_user.message(F.text=='👀 Список', AdminState.admin_actions)
async def get_list_users(message: Message, state: FSMContext):

    with Session.begin() as session:
        user_ids = session.scalars(select(User.id)).all()

        if not user_ids:
            await message.answer('Сейчас нет ниодного пользователя!')
            return
        
        response = f'Вот информация о пользователях:\n\n'
        for user_id in user_ids:
            user = session.get(User, user_id)
            
            response += f'- {user.name}, {user.id}\n'
        
        await message.answer(response)



@work_with_user.message(F.text.in_(['⛔ Заблокировать', '✅ Разблокировать']), AdminState.admin_actions)
async def block_or_unblock_user(message: Message, state: FSMContext):

    if message.text == '⛔ Заблокировать':

        admin_id = message.from_user.id
        with Session.begin() as session:

            user_ids = session.scalars(select(User.id).filter(User.block_status==False, User.id != admin_id)).all()
            kb = InlineKeyboardBuilder()
            if not user_ids:

                await message.answer('Сейчас нет ниодного пользователя!')
                return
            
            for user_id in user_ids:
                user = session.get(User, user_id)
                
                kb.button(text=f'{user.name}', callback_data=f'block_user:{user.id}')
            
            kb = kb.as_markup()
            await message.answer('Выберите пользователя которого хотите заблокировать:', reply_markup=kb)

    elif message.text == '✅ Разблокировать':
        with Session.begin() as session:

            user_ids = session.scalars(select(User.id).filter(User.block_status==True)).all()
            kb = InlineKeyboardBuilder()
            if not user_ids:

                await message.answer('Сейчас нет ниодного пользователя!')
                return
            
            for user_id in user_ids:
                user = session.get(User, user_id)
                
                kb.button(text=f'{user.name}', callback_data=f'un_block_user:{user.id}')
            
            kb = kb.as_markup()
            await message.answer('Выберите пользователя которого хотите разблокировать:', reply_markup=kb)



@work_with_user.callback_query(F.data.startswith('block_user'))
async def blocked_user(callback: CallbackQuery, state: FSMContext, bot: Bot):

    try:

        await callback.answer()
        user_id = callback.data.split(':')[1]

        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_audios=False,
            can_send_photos=False,
        )

        chanel_user_name = 'TakeGunasf'

        await bot.restrict_chat_member(chat_id=await get_channel_id(bot, chanel_user_name), user_id=user_id, permissions=permissions)

        with Session.begin() as session:
            user = session.get(User, user_id)
            if user:
                user.block_status = True
            
            else:
                await callback.message.answer('Пользователь не найден!')
                return

        await callback.message.reply('Вы заблокали')

    except Exception as e:
        print(e)
        await callback.message.reply('Не удалось заблокировать пользователя!')

@work_with_user.callback_query(F.data.startswith('un_block_user:'))
async def un_blocked_user(callback: CallbackQuery, state: FSMContext, bot: Bot):

    try:
        
        await callback.answer()
        user_id = callback.data.split(':')[1]

        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_photos=True,
        )

        chanel_user_name = 'TakeGunasf'

        await bot.restrict_chat_member(chat_id=await get_channel_id(bot, chanel_user_name), user_id=user_id, permissions=permissions)
        await callback.message.reply('Вы разаблокали')

        with Session.begin() as session:
            user = session.get(User, user_id)
            if user:
                user.block_status = False
            else:
                await callback.message.answer('Пользователь не найден!')
                return

    except Exception as e:
        print(e)
        await callback.message.edit_text('Не удалось разблокировать пользователя!')