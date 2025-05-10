from sqlalchemy import select
from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext

from aiogram.types import (
    message,
    Message,
    ReplyKeyboardRemove,
)

from ...keyboards.reply import admin_main_menu, settings_menu
from ...database import (Session,
                        User,)


from ...utils.states import AdminState


settings_router = Router()

@settings_router.message(F.text=='📢 Рассылка', AdminState.admin_actions)
async def ping_everyone(message: Message, state: FSMContext):

    admin_id = message.from_user.id 
    try:

        with Session.begin() as session:
            user_ids = session.scalars(select(User.id).filter(User.id != admin_id)).all()

            if not user_ids:
                await message.answer('Нет пользователей для оповещения!')
                return

        await message.answer('Введите текст рассылки!', reply_markup=ReplyKeyboardRemove())
        await state.set_state(AdminState.ping_text)

    except Exception as e:
        await message.answer('Не удалось сделать рассылку!')
        return

@settings_router.message(F.text, AdminState.ping_text)
async def get_text(message: Message, state: FSMContext, bot: Bot):

    admin_id = message.from_user.id
    try:

        with Session.begin() as session:
            user_ids = session.scalars(select(User.id).filter(User.id != admin_id)).all()

            succsed = 0
            failed = 0

            try:

                for user_id in user_ids:

                    await bot.send_message(
                        chat_id=user_id,
                        text=message.text
                        )
                    
                    succsed += 1

            except Exception as e:
                failed += 1
            
            print(f'{succsed}\nP{failed}')

        await message.answer(f'Было оповещено {succsed} пользователей', reply_markup=settings_menu)
        await state.set_state(AdminState.admin_actions)
    
    except Exception as e:
        await message.answer('Не удалось сделать рассылку!')
        await state.set_state(AdminState.admin_actions)
        return
