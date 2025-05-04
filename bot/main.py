import os 
import sys 
from dotenv import load_dotenv, find_dotenv
from aiogram.types import message, Message
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher

from .database import (
    Participation,
    User,
    Giveaway,
    Session,
    up,
    drop
)

from .handlers import (
    user_router,
    admin_router,
)

from .handlers.admin.raffles import admin_router_raffles

from .keyboards.reply import user_menu_keyboard

load_dotenv(find_dotenv())

dp = Dispatcher()

@dp.message(CommandStart())
async def add_user_from_db(message: Message):

    user_id = message.from_user.id
    try:

        with Session.begin() as session:
            user = session.get(User, user_id)
            if not user:
                user_name = message.from_user.username or 'user'
                add_user = User(id=user_id, name=user_name)
                session.add(add_user)
                await message.answer('Добро пожаловать!', reply_markup=user_menu_keyboard)
            
            else:
                await message.answer('Здравствуй!', reply_markup=user_menu_keyboard)
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
        admin_router_raffles
    )
    await dp.start_polling(bot)


