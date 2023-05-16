from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('🍽 Меню').insert('🛍 Корзина').add('📞 Контакты').insert('📍 Адрес и режим работы').add('↗️ ВК и Instagram').insert('❓ Помощь')

main_admin = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin.add('🍽 Меню').insert('🛍 Корзина').add('📞 Контакты').insert('📍 Адрес и режим работы').add('↗️ ВК и Instagram').insert('❓ Помощь').insert('Админ-панель')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('Добавить блюдо').add('Удалить блюдо').add('Вернуться к главному меню')

catalog_list = InlineKeyboardMarkup(row_width=1)
catalog_list.add(InlineKeyboardButton(text='Завтрак', callback_data='breakfast'),
                 InlineKeyboardButton(text='Основное меню', callback_data='main_menu'),
                 InlineKeyboardButton(text='Выпечка и десерты', callback_data='pastries/desserts'),
                 InlineKeyboardButton(text='Напитки', callback_data='drinkables'))

catalog_list_menu = InlineKeyboardMarkup(row_width=1)
catalog_list_menu.add(InlineKeyboardButton(text='Завтрак', callback_data='menu_breakfast'),
                      InlineKeyboardButton(text='Основное меню', callback_data='menu_main_menu'),
                      InlineKeyboardButton(text='Выпечка и десерты', callback_data='menu_pastries/desserts'),
                      InlineKeyboardButton(text='Напитки', callback_data='menu_drinkables'))

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Отмена')

delivery_type_buttons = ReplyKeyboardMarkup(resize_keyboard=True)
delivery_type_buttons.add("Самовывоз").add("Доставка").add('Отменить оформление')

