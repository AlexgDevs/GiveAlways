import os 
import sys 
from dotenv import load_dotenv, find_dotenv
from aiogram.types import message, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher
from .utils.states import UserState

from .database import (
    Participation,
    User,
    Giveaway,
    Session,
    up,
    drop
)

from .handlers import (
    admin_router,
    user_router,
    admin_router_raffles,
    active_raffels_router
)


from .keyboards.reply import user_menu_keyboard


load_dotenv(find_dotenv())

dp = Dispatcher()

@dp.message(CommandStart())
async def add_user_from_db(message: Message, state: FSMContext):

    user_id = message.from_user.id
    try:

        with Session.begin() as session:
            user = session.get(User, user_id)
            if not user:
                user_name = message.from_user.username or 'user'
                add_user = User(id=user_id, name=user_name)
                session.add(add_user)
                await message.answer('Добро пожаловать!', reply_markup=user_menu_keyboard)
                await state.set_state(UserState.user_actions)
            
            else:
                await message.answer('Здравствуй!', reply_markup=user_menu_keyboard)
                await state.set_state(UserState.user_actions)
                return
            
    except Exception as e:
        print(e)
        await message.answer('Ошибка сервера')
        return
    
async def main():
    bot = Bot(token=os.getenv('TOKEN'))
    # drop()
    up()
    
    dp.include_routers(
        user_router,
        admin_router,
        admin_router_raffles,
        active_raffels_router
    )
    await dp.start_polling(bot)


