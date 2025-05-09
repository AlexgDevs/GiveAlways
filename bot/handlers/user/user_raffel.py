import asyncio
from datetime import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
                    message,
                    Message,
                    CallbackQuery,
                    callback_query
                    )
from sqlalchemy import select

from ...database import Session, Giveaway, User, Participation
from ...keyboards.reply import user_menu_keyboard
from ...utils.states import UserState

user_raffels = Router()



@user_raffels.message(F.text=='🏆 Мои победы', UserState.user_actions)
async def get_list_user_giveaways(message: Message, state: FSMContext, bot: Bot):

    user_id = message.from_user.id
    with Session.begin() as session:
        user = session.get(User, user_id)
        if user:
                
                giveaways_ids = session.scalars(select(Giveaway.id).filter(Giveaway.winner_id==user_id)).all()

                if not giveaways_ids:
                    await message.answer('Вы не выиграли ниодного розыгрыша!')
                    return
                
                for giveaway_id in giveaways_ids:
                    giveaway = session.get(Giveaway, giveaway_id)

                    await bot.send_photo(
                        chat_id=user_id,
                        photo=giveaway.photo,
                        caption=f'{giveaway.title}\n\n{giveaway.description}'
                    )
                    await message.answer('Ваши победы в этих розыгрышах')
        else:
            await message.answer('Пользователь не найден')
            return