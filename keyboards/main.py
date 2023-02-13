from telebot import types

return_keyboard = types.InlineKeyboardMarkup()
return_btn = types.InlineKeyboardButton(text='Назад', callback_data='back_to_startMessage')
return_keyboard.add(return_btn)

admin_return_btn = types.InlineKeyboardButton(text='Назад', callback_data='back_to_AdminPanel')

cat_and_prod_kb = types.InlineKeyboardMarkup(row_width=1)
cp_btn1 = types.InlineKeyboardButton(text='Добавить категорию', callback_data='register_new_category')
cp_btn2 = types.InlineKeyboardButton(text='Добавить продукт', callback_data='register_new_product')
cp_btn3 = types.InlineKeyboardButton(text='Удалить категорию', callback_data='delete_category')
cp_btn4 = types.InlineKeyboardButton(text='Удалить продукт', callback_data='delete_product')
cp_btn5 = types.InlineKeyboardButton(text='Изменить данные о продукте', callback_data='change_product_info')
cat_and_prod_kb.add(cp_btn1, cp_btn2, cp_btn3, cp_btn4, cp_btn5, admin_return_btn)

