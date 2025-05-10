from datetime import datetime
import random

from sqlalchemy import func, select
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.types import (
    message,
    Message,
    ReplyKeyboardRemove,
    callback_query,
    CallbackQuery
)

import bot

from ...utils.states import AdminState
from ...keyboards.reply import admin_main_menu
from ...keyboards.inline import condition_buttons
from ...database import (Session,
                        User,
                        Giveaway,
                        Participation)

finished_raffel_router = Router()





@finished_raffel_router.message(F.text=='🛑 Завершить', AdminState.admin_actions)
async def get_list_raffel(message: Message, state: FSMContext):

    with Session.begin() as session:

        raffels_ids = session.scalars(select(Giveaway.id).filter(Giveaway.is_finished==False, Giveaway.end_data>datetime.now())).all()

        if not raffels_ids:
            await message.answer('У вас нет розыгрышей')
            return
        
        active_raffels_menu = InlineKeyboardBuilder()
        for raffel_id in raffels_ids:
            raffel = session.get(Giveaway, raffel_id)
            active_raffels_menu.button(text=f'{raffel.title}', callback_data=f'active_raffel_ahead_of_schedule:{raffel.id}')
        active_raffels_menu.adjust(1)
        act = active_raffels_menu.as_markup()
        await message.answer('Выберите розыгрыш который хотите завершить досрочно:\n\n(Учтите, розыгрыш уже начался, и чтобы все было чесно, победитель выберится автоматически!)', reply_markup=act)


@finished_raffel_router.callback_query(F.data.startswith('active_raffel_ahead_of_schedule:'))
async def get_winner_and_stop_raffel(callback: CallbackQuery, state: FSMContext, bot: Bot):

    await callback.answer()
    raffel_id = callback.data.split(':')[1]

    with Session.begin() as session:
        random_participation_ids = session.scalars(select(Participation.user_id).filter(Participation.giveaway_id==raffel_id)).all()
        raffel = session.get(Giveaway, raffel_id)

        if not random_participation_ids:
            await callback.message.answer('В данном розыгрыше нет участников!')
            return
        

        winner_id = random.choice(random_participation_ids)

        winner = session.get(User, winner_id)
        if winner and raffel:
            
            winner.won_giveaways.append(raffel)

            await bot.send_message(
                chat_id=winner.id,
                text='Ты победитель'
            )

            user_ids = session.scalars(select(User.id)).all()
            succsed = 0
            failed = 0

            await callback.message.edit_text(f'Был выбран - @{winner.name}')

            try:

                for user_id in user_ids:
                    await bot.send_message(
                        chat_id=user_id,
                        text=f'Победитель розыгрыша @{winner.name}!'
                    )
                    succsed += 1

            except Exception as e:
                print(e)
                failed += 1

            print(f'Succsed - {succsed}\n Failed - {failed}')

            raffel.is_finished = True
