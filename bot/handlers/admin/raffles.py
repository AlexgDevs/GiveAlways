import asyncio
from datetime import datetime
import json

from sqlalchemy import select
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

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

# raffles_menu.button(text='🛑 Завершить')
# raffles_menu.button(text='✏️ Изменить')
# raffles_menu.button(text='📋 Список')
# raffles_menu.button(text='⬅️ Назад')




from ...utils.states import AdminState

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

    except Exception as e:
        print(e)


@admin_router_raffles.callback_query(F.data=='req_subscribe', AdminState.raffles_requirements)
async def update_for_chanel(callback: CallbackQuery, state: FSMContext):

    await callback.answer()
    await callback.message.edit_text('Введите канал.\n Пример: @chanel')
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
                

    except ValueError:
        await message.answer('Неверный формат даты.')
        return
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}') 
        return



