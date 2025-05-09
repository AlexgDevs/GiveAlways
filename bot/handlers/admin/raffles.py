import asyncio
from datetime import datetime
import json

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
    CallbackQuery
)

from ...keyboards.reply import admin_main_menu
from ...keyboards.inline import condition_buttons
from ...database import (Session,
                        User,
                        Giveaway)


from ...utils.states import AdminState, RaffelChangeState

admin_router_raffles = Router()

# created raffles
@admin_router_raffles.message(F.text=='➕ Создать', AdminState.admin_actions)
async def set_title(message: Message, state: FSMContext):

    await message.answer('Введите название предмета который вы разыгрываете', reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminState.raffles_title)

@admin_router_raffles.message(F.text, AdminState.raffles_title)
async def get_title_and_set_description(message: Message, state: FSMContext):

    title = message.text
    if len(title) >= 256:
        await message.answer('Слишком много букв!')
        return
    
    await state.update_data(title=title)
    await message.answer('Ведите описание предмета который разыгрываете')
    await state.set_state(AdminState.raffles_description)


@admin_router_raffles.message(F.text, AdminState.raffles_description)
async def get_description_and_get_photo(message: Message, state: FSMContext):
    
    description = message.text
    if len(description) >= 896:
        await message.answer('Слишком много букв!')
        return
    
    await state.update_data(description=description)
    await message.answer('Прикрепите фотографию предмета')
    await state.set_state(AdminState.raffles_photo)

@admin_router_raffles.message(F.photo, AdminState.raffles_photo)
async def get_photo_and_set_end_data(message: Message, state: FSMContext):

    photo = message.photo[-1].file_id
    await state.update_data(photo=photo)

    await message.answer('Нпишите конечную дату розыгрыша в формате ДД.ММ.ГГГГ')
    await state.set_state(AdminState.raffles_end_date)


@admin_router_raffles.message(F.text, AdminState.raffles_end_date)
async def progress_end_data(message: Message, state: FSMContext, bot: Bot):
    try:
        end_data_str = message.text.strip()
        date_format = "%d.%m.%Y"
        end_data = datetime.strptime(end_data_str, date_format)

        if end_data <= datetime.now():
            await message.answer('Дата не может быть в прошлом!')
            return
        
        await state.update_data(end_data=end_data)
        await message.answer(f'Дата окончания: {end_data}.')
        await message.answer('Выберите 1 условие', reply_markup=condition_buttons)
        await state.set_state(AdminState.raffles_requirements)

    except ValueError:
        await message.answer('Неверный формат даты.')
        return

    except Exception as e:
        print(e)


@admin_router_raffles.callback_query(F.data=='req_subscribe', AdminState.raffles_requirements)
async def update_for_chanel(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    await callback.message.edit_text('Введите канал.\n Пример: https://t.me/TakeGunasf')
    await state.set_state(AdminState.raffles_requirements)

# @admin_router_raffles.callback_query(F.data=='')
# @admin_router_raffles.callback_query(F.data=='')
# @admin_router_raffles.callback_query(F.data=='')


@admin_router_raffles.message(F.text, AdminState.raffles_requirements)
async def get_name_chanel(message: Message, state: FSMContext, bot: Bot):

    requirements = message.text
    if requirements.startswith('@'):
        await message.answer('Канал не может начинаться с @')
        return
    
    requirements_username = requirements.split('/')[-1].replace('@', '').strip()
    await state.update_data(requirements=requirements_username)

    try:
        
        user_id = message.from_user.id
        state_data = await state.get_data()
        end_data = state_data.get('end_data')
        title = state_data.get('title')
        description = state_data.get('description')
        photo = state_data.get('photo')

        with Session.begin() as session:
            try:
                user = session.get(User, user_id)
                if user:
                    new_giveaway = Giveaway(

                        title=title,
                        description=description,
                        photo=photo,
                        end_data=end_data,
                        requirements=requirements_username,
                        creator_id=user_id
                    )

                    session.add(new_giveaway)
                    await message.answer('Вы успешно создали розыгрыш!', reply_markup=admin_main_menu)
                    await state.clear()
                    await state.set_state(AdminState.admin_actions)

                    

                    user_ids = session.scalars(select(User.id)).all()
                    succsed = 0
                    failed = 0

                    for user_id in user_ids:
                            
                        try:

                            await bot.send_photo(
                                chat_id=user_id,
                                photo=photo,
                                caption=f'был создан розыгрыш!\n\n{title}\n\n{description}\n\nДата окончание розыгрыша в {end_data}\nУспей поучаствовать!'
                            )

                            succsed += 1
                            await asyncio.sleep(0.3)
                            
                        except Exception as e:
                            print('failed', e)
                            failed += 1

                    print(f'{succsed}\n{failed} - ')

            except Exception as e:
                await message.answer(f'Не удалось создать розыгрыш! - {e}', reply_markup=admin_main_menu)
                await state.clear()
                await state.set_state(AdminState.admin_actions)
                

    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}') 
        return
    


@admin_router_raffles.message(F.text=='✏️ Изменить', AdminState.admin_actions)
async def get_change_raffel_menu(message: Message, state: FSMContext):

    dicret_menu = ReplyKeyboardBuilder()
    for i in range(1, 5):
        dicret_menu.button(text=f'{i}')
    dicret_menu = dicret_menu.adjust(4).as_markup(resize_keyboard=True)

    await message.answer('''
1. Изменить фото
2. Изменить описание
3. Изменить дату розыгрыша
4. Назад
''', reply_markup=dicret_menu)
    await state.set_state(RaffelChangeState.raffel_action)


@admin_router_raffles.message(F.text.in_(str([1, 2, 3, 4])), RaffelChangeState.raffel_action)
async def select_change(message: Message, state: FSMContext):

    if message.text == '1':

        with Session.begin() as session:
            raffels_ids = session.scalars(select(Giveaway.id)).all()

            if not raffels_ids:
                await message.answer('Сейчас нет розыгрышей')
                return
            
            for raffel_id in raffels_ids:
                raffel = session.get(Giveaway, raffel_id)
                raffels_menu = InlineKeyboardBuilder()
                raffels_menu.button(text=f'{raffel.title}', callback_data=f'raffel_photo_id:{raffel_id}')
            
            raffels_menu = raffels_menu.adjust(3).as_markup()
            await message.answer('Выберите для какого розыгрыша вы хотите изменить фото', reply_markup=raffels_menu)



    elif message.text == '2':

        with Session.begin() as session:
            raffels_ids = session.scalars(select(Giveaway.id)).all()

            if not raffels_ids:
                await message.answer('Сейчас нет розыгрышей')
                return
            
            for raffel_id in raffels_ids:
                raffel = session.get(Giveaway, raffel_id)
                raffels_menu = InlineKeyboardBuilder()
                raffels_menu.button(text=f'{raffel.title}', callback_data=f'raffel_description_id:{raffel_id}')
            
            raffels_menu = raffels_menu.adjust(3).as_markup()
            await message.answer('Выберите для какого розыгрыша вы хотите изменить описание', reply_markup=raffels_menu)

    
    elif message.text == '3':

        with Session.begin() as session:
            raffels_ids = session.scalars(select(Giveaway.id)).all()

            if not raffels_ids:
                await message.answer('Сейчас нет розыгрышей')
                return
            
            for raffel_id in raffels_ids:
                raffel = session.get(Giveaway, raffel_id)
                raffels_menu = InlineKeyboardBuilder()
                raffels_menu.button(text=f'{raffel.title}', callback_data=f'raffel_end_data_id:{raffel_id}')
            
            raffels_menu = raffels_menu.adjust(3).as_markup()
            await message.answer('Выберите для какого розыгрыша вы хотите изменить окончание даты', reply_markup=raffels_menu)

    elif message.text == '4':
        await message.answer('Вы вернулись в админ меню', reply_markup=admin_main_menu)

    else:
        await message.answer('Нет такого ответа!')

@admin_router_raffles.callback_query(F.data.startswith('raffel_photo_id:'))
async def awaitng_change_description(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    raffel_id = callback.data.split(':')[1]
    await state.update_data(raffel_id=raffel_id)
    await callback.message.edit_text('Скиньте новое фото')
    await state.set_state(RaffelChangeState.raffel_change_photo)


@admin_router_raffles.message(F.photo, RaffelChangeState.raffel_change_photo)
async def update_change(message: Message, state: FSMContext):

    data = await state.get_data()
    raffel_id = data.get('raffel_id')

    with Session.begin() as session:
        raffel = session.get(Giveaway, raffel_id)
        raffel.photo = message.photo[-1].file_id
        await message.answer('Измениения успешны!')
        await state.clear()
        return await get_change_raffel_menu(message, state)



@admin_router_raffles.callback_query(F.data.startswith('raffel_description_id:'))
async def awaitng_change_description(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    raffel_id = callback.data.split(':')[1]
    await state.update_data(raffel_id=raffel_id)
    await callback.message.edit_text('Введите новое описание')
    await state.set_state(RaffelChangeState.raffel_change_description)


@admin_router_raffles.message(F.text, RaffelChangeState.raffel_change_description)
async def update_change(message: Message, state: FSMContext):

    data = await state.get_data()
    raffel_id = data.get('raffel_id')

    with Session.begin() as session:
        raffel = session.get(Giveaway, raffel_id)
        raffel.description = message.text
        await message.answer('Измениения успешны!')
        await state.clear()
        return await get_change_raffel_menu(message, state)
    


@admin_router_raffles.callback_query(F.data.startswith('raffel_end_data_id:'))
async def awaitng_change_description(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    raffel_id = callback.data.split(':')[1]
    await state.update_data(raffel_id=raffel_id)
    await callback.message.edit_text('Нпишите конечную дату розыгрыша в формате ДД.ММ.ГГГГ')
    await state.set_state(RaffelChangeState.raffel_change_end_data)


@admin_router_raffles.message(F.text, RaffelChangeState.raffel_change_end_data)
async def update_change(message: Message, state: FSMContext):

    data = await state.get_data()
    raffel_id = data.get('raffel_id')

    end_data_str = message.text.strip()
    date_format = "%d.%m.%Y"
    end_data = datetime.strptime(end_data_str, date_format)

    if end_data <= datetime.now():
        await message.answer('Дата не может быть в прошлом!')
        return

    with Session.begin() as session:
        raffel = session.get(Giveaway, raffel_id)
        raffel.end_data = end_data
        await message.answer('Измениения успешны!')
        await state.clear()
        return await get_change_raffel_menu(message, state)







@admin_router_raffles.message(F.text=='📋 Список', AdminState.admin_actions)
async def get_list_active_raffels(message: Message, state: FSMContext, bot: Bot):

    with Session.begin() as session:
        raffels_ids = session.scalars(select(Giveaway.id).filter(Giveaway.end_data>datetime.now())).all()
        user_id = message.from_user.id

        if not raffels_ids:
            await message.answer('Сейчас нет активных розыгрышей')
            return
        
        total = 0

        for raffel_id in raffels_ids:
            total += 1

            raffel = session.get(Giveaway, raffel_id)
            await bot.send_photo(
                chat_id=user_id,
                photo=raffel.photo,
                caption=f'{raffel.title}\n\n{raffel.description}\n\nСписок участников - {raffel.user_total}\n\nДата окончания - {raffel.end_data}'
            )

        await message.answer(f'Всего - {total} розыгрышей!')











