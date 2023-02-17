from config import bot, cursor, db, admin_chat
from telebot import types
from keyboards import main as kb_main

def buy_all_products(callback):
    bot.edit_message_text(text='Заявка отправлена! Ждите своих товаров.', chat_id=callback.message.chat.id, 
    message_id=callback.message.id, reply_markup=kb_main.return_keyboard)
    cursor.execute(f'''SELECT 
    shop_basket.product_id,
    shop_basket.cost, 
    products.product_name FROM shop_basket 
    INNER JOIN products ON shop_basket.product_id = products.id 
    WHERE user_id = {callback.from_user.id}''')
    all_products = cursor.fetchall()
    products_names = ''
    total_cost = 0
    buy_kb = types.InlineKeyboardMarkup()
    buy_btn1 = types.InlineKeyboardButton(text='✅', callback_data=f'accept_user_buy_{callback.from_user.id}')
    buy_btn2 = types.InlineKeyboardButton(text='❌', callback_data=f'deny_user_buy_{callback.from_user.id}')
    buy_kb.add(buy_btn1, buy_btn2)
    for product_id, cost, product_name in all_products:
        products_names += f'{product_name}\n'
        total_cost += cost
    bot.send_message(admin_chat, f'''Покупатель: {callback.from_user.username}
Продукты:
{products_names}
Итого: {total_cost}''', reply_markup=buy_kb, parse_mode='html')
    cursor.execute(f'''DELETE FROM shop_basket WHERE user_id = {callback.from_user.id}''')


def admin_buy_choice(callback):
    choice = callback.data.split('_')[0]
    user_id = callback.data.split('_')[-1]
    if choice == 'accept':
        bot.send_message(user_id, 'Логин:Пароль', reply_markup=kb_main.prod_delivery_kb)
    if choice == 'deny':
        bot.send_message(user_id, 'Извините, товара нет в наличии.\nПопробуйте еще раз позже.', reply_markup=kb_main.return_keyboard)


def add_to_logins(callback):
    message = callback.message.text
    bot.delete_message(callback.message.chat.id, callback.message.id)
    logins_info = message.split('\n')
    for info in logins_info:
        add_info = info.split(':')
        cursor.execute(f'''INSERT INTO user_logins(user_id, login, password, product_name) VALUES({callback.from_user.id}, 
        '{add_info[0]}', '{add_info[1]}', 'Имя продукта');''')
        db.commit()

def bot_register_buy_system_handlers():
    bot.register_callback_query_handler(buy_all_products, func=lambda callback: callback.data == 'buy_all_products')
    bot.register_callback_query_handler(admin_buy_choice, func=lambda callback: '_user_buy_' in callback.data)
    bot.register_callback_query_handler(add_to_logins, func=lambda callback: callback.data == 'product_delivery_accept')