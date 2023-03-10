from telebot import types

admin_return_btn = types.InlineKeyboardButton(text='Назад', callback_data='back_to_AdminPanel')
return_btn = types.InlineKeyboardButton(text='Назад', callback_data='back_to_startMessage')

admin_menu_keyboard = types.InlineKeyboardMarkup(row_width=1)
admin_menu_btn1 = types.InlineKeyboardButton(text='Настройки категорий и продуктов', callback_data='step_to_cp_settings')
admin_menu_btn2 = types.InlineKeyboardButton(text='Настройки администратора', callback_data='step_to_admin_settings')
admin_menu_keyboard.add(admin_menu_btn1, admin_menu_btn2, return_btn)
