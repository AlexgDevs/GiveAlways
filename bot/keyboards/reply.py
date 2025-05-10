from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Главное меню админа
admin_main_menu = ReplyKeyboardBuilder()
admin_main_menu.button(text='🎁 Розыгрыши') #.
admin_main_menu.button(text='👥 Пользователи') #.
admin_main_menu.button(text='📊 Статистика')
admin_main_menu.button(text='⚙️ Настройки')
admin_main_menu.button(text='⬅️ Главное меню') #. 
admin_main_menu.adjust(2, 2, 1)
admin_main_menu = admin_main_menu.as_markup(resize_keyboard=True)

# Меню розыгрышей
raffles_menu = ReplyKeyboardBuilder()
raffles_menu.button(text='➕ Создать') #.
raffles_menu.button(text='🛑 Завершить') #.
raffles_menu.button(text='✏️ Изменить') #. 
raffles_menu.button(text='📋 Список') #.
raffles_menu.button(text='⬅️ Назад') #.
raffles_menu.adjust(2, 2, 1)
raffles_menu = raffles_menu.as_markup(resize_keyboard=True)


# create
raffel_back = ReplyKeyboardBuilder()
raffel_back.button(text='Отменить создание')
raffel_back = raffel_back.as_markup(resize_keyboard=True)

# Меню пользователей
users_menu = ReplyKeyboardBuilder()
users_menu.button(text='⛔ Заблокировать') #. 
users_menu.button(text='✅ Разблокировать') #.
users_menu.button(text='👀 Список') #.
users_menu.button(text='⬅️ Назад') #.
users_menu.adjust(2, 2)
users_menu = users_menu.as_markup(resize_keyboard=True)

# Меню статистики
stats_menu = ReplyKeyboardBuilder()
stats_menu.button(text='📈 Общая')
stats_menu.button(text='📊 По розыгрышу')
stats_menu.button(text='📁 Экспорт')
stats_menu.button(text='⬅️ Назад') #.
stats_menu.adjust(2, 2)
stats_menu = stats_menu.as_markup(resize_keyboard=True)

# Меню настроек
settings_menu = ReplyKeyboardBuilder()
settings_menu.button(text='📢 Рассылка') #.
settings_menu.button(text='⚙️ Параметры')
settings_menu.button(text='⬅️ Назад') #.
settings_menu.adjust(2, 2)
settings_menu = settings_menu.as_markup(resize_keyboard=True)

############################################
user_menu_keyboard = ReplyKeyboardBuilder()
user_menu_keyboard.button(text='🎯 Мое участие') #.
user_menu_keyboard.button(text='🎁 Активные розыгрыши') #.
user_menu_keyboard.button(text='🏆 Мои победы') #.
user_menu_keyboard.button(text='📜 Правила') #.
user_menu_keyboard.button(text='🛟 Поддержка')
user_menu_keyboard.button(text='🔔 Уведомления')
user_menu_keyboard.adjust(2)
user_menu_keyboard = user_menu_keyboard.as_markup(resize_keyboard=True,
                                                input_field_placeholder='Выберите действие...')