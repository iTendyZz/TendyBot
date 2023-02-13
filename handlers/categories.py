from config import bot, cursor, db
from telebot import types
from keyboards import main as kb_main
from handlers import main as hand_main


def register_category_request(callback):
    sent = bot.send_message(callback.message.chat.id, 'Введите название категории')
    bot.register_next_step_handler(sent, register_category, callback.message.text)


def register_category(sent, message):
    new_category = message.text
    
    cursor.execute('''SELECT name FROM categories''')
    categories = cursor.fetchall()
    if new_category not in categories:
        cursor.execute(f'''INSERT INTO categories(name) VALUES('{new_category}'); ''')
        db.commit()
        bot.send_message(message.chat.id, 'Категория добавлена!')
    else:
        bot.send_message(message.chat.id, 'Такая категория уже есть!', reply_markup=kb_main.return_keyboard)


def delete_category(callback):
    pass
    

def display_categories(callback):
    category_kbd = types.InlineKeyboardMarkup(row_width=1) 
    cursor.execute('''SELECT * FROM categories''')
    categories = cursor.fetchall()
    
    for category_id, category_name in categories:
        category_btn = types.InlineKeyboardButton(text=f'{category_name}', callback_data=f'choose_category_{category_id}')
        category_kbd.add(category_btn)
    category_btn_back = types.InlineKeyboardButton(text='Назад', callback_data='return_to_menu')
    category_kbd.add(category_btn_back)
    
    bot.edit_message_text(chat_id=callback.message.chat.id, text='Вот наши категории:', message_id=callback.message.id, 
    reply_markup=category_kbd)


def back_to(callback):
    back = callback.data.split('_')[-1]
    if back == 'menu' or back == 'startMessage':
        hand_main.start_message(callback.message)
    if back == 'catalog' or back == 'products':
        display_categories(callback)


def display_products(callback):
    category_id = int(callback.data.split('_')[-1])
    cursor.execute(f'''SELECT id, product_name FROM products WHERE category = {category_id}''')
    products = cursor.fetchall()
    
    product_kbd = types.InlineKeyboardMarkup(row_width=1)

    for product_id, product_name in products:
        product_btn = types.InlineKeyboardButton(text=f'{product_name}', callback_data=f'choose_product_{product_id}')
        product_kbd.add(product_btn)
    product_btn_back = types.InlineKeyboardButton(text='Назад', callback_data='return_to_catalog')
    product_kbd.add(product_btn_back)
    
    bot.edit_message_text(chat_id=callback.message.chat.id, text='А вот и продукты:', message_id=callback.message.id, 
    reply_markup=product_kbd)


def display_product_info(callback):
    product_id = int(callback.data.split('_')[-1])
    cursor.execute(f'''SELECT * FROM products WHERE id = {product_id}''')
    product_info = cursor.fetchone()
    description = product_info[5]

    product_kbd = types.InlineKeyboardMarkup(row_width=1)
    product_btn1 = types.InlineKeyboardButton(text='Добавить в корзину', callback_data=f'add_to_basket_{product_info[0]}')
    product_btn2 = types.InlineKeyboardButton(text='Назад', callback_data='return_to_products')
    product_kbd.add(product_btn1, product_btn2)

    if description is None:
        description = 'Описание отсутствует'
    bot.edit_message_text(text=f'''<u>Продукт</u>: {product_info[1]}
<u>Цена</u>: <s>{product_info[2]}</s> <b>{product_info[3]}</b>
<u>Описание</u>: {description}''', parse_mode='html', chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=product_kbd)


def add_to_shop_basket(callback):
    product_id = int(callback.data.split('_')[-1])
    cursor.execute(f'''SELECT price_max_disсount FROM products WHERE id = {product_id}''')
    product_cost = cursor.fetchone()[0]
    cursor.execute(f'''INSERT INTO shop_basket(user_id, product_id, cost) VALUES({callback.from_user.id}, 
    {product_id}, {product_cost})''')
    db.commit()
    bot.edit_message_text(text='<b>Продукт добавлен в корзину</b>', chat_id=callback.message.chat.id,
    message_id=callback.message.id, reply_markup=kb_main.return_keyboard, parse_mode='html')


def display_shop_basket(callback):
    cursor.execute(f'''SELECT products.product_name, shop_basket.cost, shop_basket.id FROM shop_basket
    INNER JOIN products on shop_basket.product_id = products.id 
    WHERE shop_basket.user_id = {callback.from_user.id}''')
    user_basket = cursor.fetchall()
    user_products = ''
    total_cost = 0
    basket_kb = types.InlineKeyboardMarkup(row_width=1)
    buy_btn = types.InlineKeyboardButton(text='Купить всё', callback_data=f'buy_all_products')
    basket_kb.add(buy_btn)
    for product_name, product_price, product_id in user_basket:
        basket_btn = types.InlineKeyboardButton(text=product_name, callback_data=f'basket_product_{product_id}')
        basket_kb.add(basket_btn)
        user_products += f'{product_name}\n'
        total_cost += product_price
    basket_kb.add(kb_main.return_btn)
    bot.edit_message_text(text=f'Вот ваш список покупок:\n{user_products}\nЕсли вы хотите убрать какой-то продукт из списка, нажмите на кнопку с его названием', 
    chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=basket_kb)
    


def bot_register_categories_handlers():
    bot.register_callback_query_handler(register_category_request, func=lambda callback: callback.data == 'register_new_category')
    bot.register_callback_query_handler(display_categories, func=lambda callback: callback.data == 'send_catalog')
    bot.register_callback_query_handler(display_products, func=lambda callback: 'choose_category_' in callback.data)
    bot.register_callback_query_handler(back_to, func=lambda callback: 'return_to_' in callback.data)
    bot.register_callback_query_handler(display_product_info, func=lambda callback: 'choose_product_' in callback.data)
    bot.register_callback_query_handler(add_to_shop_basket, func=lambda callback: 'add_to_basket_' in callback.data)
    bot.register_callback_query_handler(display_shop_basket, func=lambda callback: callback.data == 'view_shop_basket')
