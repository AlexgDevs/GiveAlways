from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    message,
    Message
)

from ...keyboards.reply import user_menu_keyboard
from ...utils.states import UserState

user_router = Router()



@user_router.message(F.text=='📜 Правила', UserState.user_actions)
async def get_rules(message: Message, state: FSMContext):

    rules_text = """
📜 <b>Правила участия</b>

🎯 <u>Как участвовать?</u>
1. Нажми «Участвовать» в розыгрыше
2. Подпишись на канал (если требуется)
3. Дождись результатов!

⚠️ <u>Важно:</u>
• Участие бесплатное
• 1 человек = 1 аккаунт

Подробнее: /faq
    """
    await message.answer(rules_text, parse_mode="HTML")


@user_router.message(F.text=='🛟 Поддержка', UserState.user_actions)
async def get_support(message: Message, state: FSMContext):

    await message.answer('<b>Вы можете связаться с нашим админом @TakeGuna.\n Не стесняйтесь задавать вопросы!</b>', parse_mode="HTML")

