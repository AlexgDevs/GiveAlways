from aiogram.utils.keyboard import ReplyKeyboardBuilder

admin_menu_keyboard = ReplyKeyboardBuilder()
admin_menu_keyboard.button(text='🎁 Розыгрыши')
admin_menu_keyboard.button(text='👥 Пользователи')
admin_menu_keyboard.button(text='📊 Статистика')
admin_menu_keyboard.button(text='⚙️ Настройки')
admin_menu_keyboard.button(text='⬅️ Назад')
admin_menu_keyboard.adjust(2, 2, 1)
admin_menu_keyboard = admin_menu_keyboard.as_markup(resize_keyboard=True)


user_menu_keyboard = ReplyKeyboardBuilder()
user_menu_keyboard.button(text='Мое участие')
user_menu_keyboard.button(text='Активные розыгрыши')
user_menu_keyboard.button(text='Правила')
user_menu_keyboard.button(text='Поддержка')
user_menu_keyboard.adjust(2)
user_menu_keyboard = user_menu_keyboard.as_markup(resize_keyboard=True)