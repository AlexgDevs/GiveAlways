from aiogram.utils.keyboard import InlineKeyboardBuilder

builder = InlineKeyboardBuilder()
builder.button(text="Подписка на канал", callback_data="req_subscribe")
builder.button(text="Репост записи", callback_data="req_repost") #pass
builder.button(text="Возраст аккаунта", callback_data="req_account_age") #pass
builder.button(text="Готово", callback_data="req_done") # pass 
builder.adjust(1)
condition_buttons = builder.as_markup()

