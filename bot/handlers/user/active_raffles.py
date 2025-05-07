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



active_raffels_router = Router()


@active_raffels_router.message(F.text=='🎁 Активные розыгрыши', UserState.user_actions)
async def get_list_raffels(message: Message, state: FSMContext, bot: Bot):
    
    user_id = message.from_user.id

    try:

        with Session.begin() as session:
            raffels_ids = session.scalars(select(Giveaway.id).filter(Giveaway.end_data > datetime.now())).all()
            
            if not raffels_ids:
                await message.answer('Сейчас нет розыгрышей')

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
                    await message.answer('Розыгрыш не найден!')
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
            
            activate_button = InlineKeyboardBuilder()
            await callback.message.answer(f'''
Прежде чем участвовать, выполните следующие условия:
1.Подпишитесь на пользователя(лей) @{raffel.requirements}
2. Нажмите на кнопку "Cделал"''',
reply_markup=activate_button.button(text='Сделал', callback_data=f'check_condition:{raffel.id}:{raffel.requirements}').adjust(1).as_markup())


async def get_channel_id(bot: Bot, channel_username: str) -> int:

    clean_username = channel_username.replace('@', '').replace('https://t.me/', '').strip().lower()    
    chat = await bot.get_chat(f"@{clean_username}")
    return chat.id


@active_raffels_router.callback_query(F.data.startswith('check_condition:'))
async def check_condition(callback: CallbackQuery, state: FSMContext, bot: Bot):

    await callback.answer()
    user_id = callback.from_user.id
    raffel_id = callback.data.split(':')[1]
    chanel_username = callback.data.split(':')[2]
    chanel_id = await get_channel_id(bot, chanel_username)

    member = await bot.get_chat_member(
        chat_id=chanel_id,
        user_id=user_id
    )

    if member.status in ['left', 'kicked', 'banned']:
        await callback.message.answer(f'Вы не выполнили все условия\nПодпишитесь на канал @{chanel_username} и нажмите кнопку участвовать')
        return

    try:
        with Session.begin() as session:

            user = session.get(User, user_id)
            raffel = session.get(Giveaway, raffel_id)
            participation = session.scalars(select(Participation).filter(user_id==user_id, raffel_id==raffel_id)).all()

            if participation:
                await callback.message.answer('Вы уже учавствуйте в данном розыгрыше!')
                return
            
            if user and raffel:

                new_participation = Participation(user_id=user_id, giveaway_id=raffel.id)
                session.add(new_participation)
                raffel.user_total += 1
                await callback.message.edit_text('Вы успешно участвуйте в розыгрыше!')
            
            else:
                await callback.message.answer('Пользователь или розыгрыш не найден')
                return
            
    except Exception as e:
        await callback.message.answer('Не удалось принять участие')
        return
    


@active_raffels_router.message(F.text=='🎯 Мое участие', UserState.user_actions)
async def get_list_participations(message: Message, state: FSMContext, bot: Bot):

    user_id = message.from_user.id
    with Session.begin() as session:
        participations_ids = session.scalars(select(Participation.id).filter(Participation.user_id==user_id)).all()

        if not participations_ids:
            await message.answer('Вы нигде не участвуйте')
            return

        for participation_id in participations_ids:
            participation = session.get(Participation, participation_id)

            if participation:

                raffel_id = participation.giveaway_id

                raffel = session.get(Giveaway, raffel_id)
                if raffel:
                    await bot.send_photo(
                        chat_id=user_id,
                        photo=raffel.photo,
                        caption=f'{raffel.title}\n\n{raffel.description}\n\nКоличество участников: {raffel.user_total}\n\nОкончание - {raffel.end_data}'
                    )
                else:
                    await message.answer('Розыгрыш не найден')
                    return
            else:
                await message.answer('Вы нигде не участвуйте')