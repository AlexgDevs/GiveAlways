from datetime import datetime

from sqlalchemy import select
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiogram.types import (
    message,
    Message,
    ReplyKeyboardRemove
)

from ...keyboards.reply import admin_main_menu
from ...database import (Session,
                        User,
                        Giveaway)

# raffles_menu.button(text='🛑 Завершить')
# raffles_menu.button(text='✏️ Изменить')
# raffles_menu.button(text='📋 Список')
# raffles_menu.button(text='⬅️ Назад')




from ...utils.states import AdminState

admin_router_raffles = Router()


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
async def progress_end_data_and_add_to_db(message: Message, state: FSMContext):
    try:
        end_data_str = message.text.strip()
        date_format = "%d.%m.%Y"
        end_data = datetime.strptime(end_data_str, date_format)

        if end_data <= datetime.now():
            await message.answer('Дата не может быть в прошлом!')
            return
        
        await message.answer(f'Дата окончания: {end_data}.')


        user_id = message.from_user.id
        state_data = await state.get_data()
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
                        creator_id=user_id
                    )

                    session.add(new_giveaway)
                    await message.answer('Вы успешно создали розыгрыш!', reply_markup=admin_main_menu)
                    await state.clear()
                    await state.set_state(AdminState.admin_actions)
            
            except Exception as e:
                await message.answer(f'Не удалось создать розыгрыш! - {e}', reply_markup=admin_main_menu)
                await state.clear()
                await state.set_state(AdminState.admin_actions)
                

    except ValueError:
        await message.answer('Неверный формат даты. Пожалуйста используйте ДД.ММ.ГГГГ')
        return
    except Exception as e:
        await message.answer(f'Произошла ошибка: {e}') 
        return


