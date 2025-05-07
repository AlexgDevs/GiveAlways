from datetime import datetime
import random

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

import bot


from ...keyboards.reply import admin_main_menu
from ...keyboards.inline import condition_buttons
from ...database import (Session,
                        User,
                        Giveaway,
                        Participation)

finished_raffel_router = Router()




