import os 
import random
import sys 
from dotenv import load_dotenv, find_dotenv
from aiogram.types import message, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram import Bot, Dispatcher
from sqlalchemy import func, select

import bot
from .utils.states import UserState
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

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
    active_raffels_router,
    finished_raffel_router,
    user_raffels,
    work_with_user,
    settings_router
)

from .keyboards.reply import user_menu_keyboard


load_dotenv(find_dotenv())
dp = Dispatcher()


scheduler = AsyncIOScheduler()
async def select_winner(giveaway_id: int, bot: Bot):

    try:

        with Session.begin() as session:
            random_participation_users_id = session.scalars(select(Participation.user_id).filter(func.random(), Participation.giveaway_id==giveaway_id).limit(1)).all()

            raffel = session.get(Giveaway, giveaway_id)
            winner = session.get(User, random_participation_users_id)

            winner.won_giveaways.append(raffel)

            await bot.send_message(
                chat_id=random_participation_users_id,
                text='Ты выиграл'
            )
    
    except Exception as e:
        print(f'Победитель не найден! - {e}')

async def check_time(bot: Bot):

    try:

        with Session.begin() as session:
            active_giveaways_ids = session.scalars(select(Giveaway.id).filter(Giveaway.end_data>datetime.now, Giveaway.is_finished==False)).all()
            
            if not active_giveaways_ids:
                return None
            
            for active_giveaway_id in active_giveaways_ids:
                giveaway = session.get(Giveaway, active_giveaway_id)

                if giveaway.end_data <= datetime.now():
                    giveaway.is_finished = True
                    await select_winner(giveaway.id, bot)
    
    except Exception as e:
        print(f'Не удалось проверить розыгрыш - {e}')



@dp.message(CommandStart())
async def add_user_from_db(message: Message, state: FSMContext):

    scheduler.add_job(
        func=check_time,
        args=(bot,),
        trigger="interval",
        minutes=60,
    )

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
        active_raffels_router,
        user_raffels,
        finished_raffel_router,
        work_with_user,
        settings_router
    )

    await dp.start_polling(bot)
