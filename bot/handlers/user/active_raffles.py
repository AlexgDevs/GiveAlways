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

from ...keyboards.inline import button_chek_condition
from ...database import Session, Giveaway
from ...keyboards.reply import user_menu_keyboard
from ...utils.states import UserState

active_raffels_router = Router()


@active_raffels_router.message(F.text=='🎁 Активные розыгрыши', UserState.user_actions)
async def get_list_raffels(message: Message, state: FSMContext, bot: Bot):
    
    user_id = message.from_user.id

    try:

        with Session.begin() as session:
            raffels_ids = session.scalars(select(Giveaway.id).filter(Giveaway.end_data > datetime.now())).all()
            for raffel_id in raffels_ids:
                raffel = session.get(Giveaway, raffel_id)
                if raffel:
                    participate_button = InlineKeyboardBuilder()
                    await bot.send_photo(
                                    chat_id=user_id,
                                    photo=raffel.photo,
                                    caption=f'розыгрыш!\n\n{raffel.title}\n\n{raffel.description}\n\nДата окончание розыгрыша в {raffel.end_data}\nУспей поучаствовать!',
                                    reply_markup=participate_button.button(text='Участвовать', callback_data=f'participate_action:{raffel.id}').adjust(1).as_markup()
                                )
                    asyncio.sleep(0.3)
                else:
                    await message.answer('Сейчас нет розыгрышей!')
                    return
    
    except Exception as e:
        print(e)
        await message.answer('Не удалось посмотреть список розыгрышей')
        return
    

@active_raffels_router.callback_query(F.data.startswith('participate_action:'))
async def chek_condition(callback: CallbackQuery):

    await callback.answer()
    raffels_id = callback.data.split(':')[1]
    
    with Session.begin() as session:
        raffel = session.get(Giveaway, raffels_id)
        if raffel:
            await callback.message.answer(f'Прежде чем участвовать, выполните следующие условия:\n1.Подпишитесь на пользователя(лей) {raffel.requirements}\n2. Нажмите на кнопку "Cделал"', reply_markup=button_chek_condition)



