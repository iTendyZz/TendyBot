from config import bot, cursor, db
from telebot import types
from keyboards import main as kb_main
from handlers import main as hand_main
from keyboards import admin as kb_admin


def register_category_request(callback):
    bot.delete_message(callback.message.chat.id, callback.message.id)
    sent = bot.send_message(callback.message.chat.id, 'Введите название категории')
    bot.register_next_step_handler(sent, register_category)


def register_category(message):
    new_category = message.text
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    cursor.execute('''SELECT name FROM categories''')
    categories = cursor.fetchall()
    if new_category not in categories:
        cursor.execute(f'''INSERT INTO categories(name) VALUES('{new_category}'); ''')
        db.commit()
        bot.send_message(message.chat.id, 'Категория добавлена!', reply_markup=kb)
    else:
        bot.send_message(message.chat.id, 'Такая категория уже есть!', reply_markup=kb_main.return_keyboard)


def delete_category_request(callback):
    cursor.execute('''SELECT * FROM categories''')
    categories = cursor.fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat_id, cat_name in categories:
        btn = types.InlineKeyboardButton(text=cat_name, callback_data=f'delete_cat_by_{cat_id}')
        kb.add(btn)
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Выберите категорию для удаления:', chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=kb)


def delete_category(callback):
    cat_id = callback.data.split('_')[-1]
    cursor.execute(f'''DELETE FROM categories WHERE id = {cat_id}''')
    db.commit()
    cursor.execute(f'''DELETE FROM products WHERE category = {cat_id}''')
    db.commit()
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Категория успешно удалена!', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


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
    cursor.execute(f'''SELECT pricemaxdisсount FROM products WHERE id = {product_id}''')
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
    buy_btn = types.InlineKeyboardButton(text='Купить всё', callback_data='buy_all_products')
    basket_kb.add(buy_btn)
    for product_name, product_price, product_id in user_basket:
        basket_btn = types.InlineKeyboardButton(text=product_name, callback_data=f'basket_product_delete_{product_id}')
        basket_kb.add(basket_btn)
        user_products += f'**{product_name}**\n'
        total_cost += product_price
    delete_all_btn = types.InlineKeyboardButton(text='Удалить все продукты', callback_data='delete_all_products_from_basket')
    basket_kb.add(delete_all_btn, kb_main.return_btn)
    bot.edit_message_text(text=f'Вот ваш список покупок:\n\n{user_products}\nИтоговая стоимость: {total_cost}\n\nЕсли вы хотите убрать какой-то продукт из списка, нажмите на кнопку с его названием', 
    chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=basket_kb, parse_mode='markdown')
    

def delete_product_from_basket(callback):
    product_id = callback.data.split('_')[-1]
    cursor.execute(f'''SELECT * FROM shop_basket WHERE id = {product_id}''')
    product_data = cursor.fetchone()
    cursor.execute(f'''DELETE FROM shop_basket WHERE id = {product_data[0]} AND 
    user_id = {product_data[1]} AND 
    product_id = {product_data[2]} AND 
    cost = {product_data[3]}''')
    bot.edit_message_text(text='Продукт успешно удален!', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb_main.return_keyboard)


def delete_all_products_from_basket(callback):
    cursor.execute(f'''SELECT * FROM shop_basket WHERE user_id = {callback.from_user.id}''')
    all_products = cursor.fetchall()
    cursor.execute(f'''DELETE FROM shop_basket WHERE user_id = {callback.from_user.id}''')
    bot.edit_message_text(text=f'Удалено {len(all_products)} продуктов!', message_id=callback.message.id, chat_id=callback.message.chat.id, 
    reply_markup=kb_main.return_keyboard)


def add_product_to_category(callback):
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    sent = bot.edit_message_text(chat_id=callback.message.chat.id, text='''Вводите данные о продукте с каждой новой строки без нумерации пунктов! Порядок:
    
Имя товара
Цена
Описание товара
Далее вам предложат выбрать категорию для товара''', message_id=callback.message.id, reply_markup=kb)
    bot.register_next_step_handler(sent, request_category_for_product, callback.message.id)


def request_category_for_product(message, main_message_id):
    prod_info = message.text.split('\n')
    bot.delete_message(message.chat.id, message.id)
    cursor.execute(f'''INSERT INTO products(product_name, price, priceMaxDiscount, description) VALUES(
    "{prod_info[0]}", 
    {prod_info[1]},
    {prod_info[1]}, 
    "{prod_info[2]}");''')
    db.commit()
    cursor.execute('''SELECT * FROM categories''')
    categories = cursor.fetchall()
    cursor.execute(f'''SELECT id FROM products WHERE product_name = "{prod_info[0]}"''')
    prod_id = cursor.fetchone()[0]
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat_id, cat_name in categories:
        btn = types.InlineKeyboardButton(text=cat_name, callback_data=f'add_new_prod_to_{cat_id}_{prod_id}')
        kb.add(btn)
    cancel = types.InlineKeyboardButton(text='Нет нужной категории', callback_data=f'cancel_adding_prod_{prod_id}')
    kb.add(cancel)
    bot.edit_message_text('Выберите категорию', message_id=main_message_id, chat_id=message.chat.id, reply_markup=kb)

        
def add_product_to_category_final(callback):
    print(callback.data)
    category = int(callback.data.split('_')[-2])
    product = int(callback.data.split('_')[-1])
    print(category, product)
    cursor.execute(f'''UPDATE products SET category = {category} WHERE id = {product}''')
    db.commit()
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Продукт успешно добавлен!', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def cancel_product(callback):
    prod = int(callback.data.split('_')[-1])
    cursor.execute(f'''DELETE FROM products WHERE id = {prod}''')
    db.commit()
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Добавление продукта отменено. Добавьте нужную вам категорию и попробуйте еще раз!', 
    chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=kb)


def choose_delete_product_category(callback):
    cursor.execute(f'''SELECT * FROM categories''')
    categories = cursor.fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for id, category in categories:
        btn = types.InlineKeyboardButton(text=category, callback_data=f'go_to_product_category_{id}')
        kb.add(btn)
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Выберите категорию', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def delete_product_from_category(callback):
    category = callback.data.split('_')[-1]
    cursor.execute(f'''SELECT id, product_name FROM products WHERE category = {category}''')
    products = cursor.fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for id, product in products:
        btn = types.InlineKeyboardButton(text=product, callback_data=f'delete_product_by_id_{id}')
        kb.add(btn)
    back = types.InlineKeyboardButton(text='Назад', callback_data='delete_product')
    kb.add(back)
    bot.edit_message_text(text='Выберите продукт', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def delete_product_from_category_final(callback):
    product = callback.data.split('_')[-1]
    cursor.execute(f'''DELETE FROM products WHERE id = {product}''')
    db.commit()
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Продукт успешно удален!', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def change_prod_info_category(callback):
    cursor.execute('''SELECT * FROM categories''')
    categories = cursor.fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for id, name in categories:
        btn = types.InlineKeyboardButton(text=name, callback_data=f'change_prod_info_by_category_{id}')
        kb.add(btn)
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Выберите категорию', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def change_prod_info_product(callback):
    category = int(callback.data.split('_')[-1])
    cursor.execute(f'''SELECT id, product_name FROM products WHERE category = {category}''')
    products = cursor.fetchall()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for id, name in products:
        btn = types.InlineKeyboardButton(text=name, callback_data=f'change_prod_info_by_prod_{id}')
        kb.add(btn)
    back = types.InlineKeyboardButton(text='Назад', callback_data='change_product_info')
    kb.add(back)
    bot.edit_message_text(text='Выберите продукт', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def choose_prod_option_request(callback):
    product = int(callback.data.split('_')[-1])
    kb = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text='Имя продукта', callback_data=f'change%prod%product_name%{product}')
    btn2 = types.InlineKeyboardButton(text='Цена', callback_data=f'change%prod%price%{product}')
    btn3 = types.InlineKeyboardButton(text='Скидка', callback_data=f'change%prod%discount%{product}')
    btn4 = types.InlineKeyboardButton(text='Категория', callback_data=f'change%prod%category%{product}')
    btn5 = types.InlineKeyboardButton(text='Описание', callback_data=f'change%prod%description%{product}')
    kb.add(btn1, btn2, btn3, btn4, btn5, kb_admin.admin_return_btn)
    bot.edit_message_text(text='Выберите редактируемый параметр', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=kb)


def change_prod_option(callback):
    option = callback.data.split('%')[-2]
    print(option)
    product = int(callback.data.split('%')[-1])
    main_message_id = callback.message.id
    if option == 'discount':
        sent = bot.send_message(callback.message.chat.id, 'Введите новое значение скидки без знака процента')
        bot.register_next_step_handler(sent, change_prod_option_final, option, product, main_message_id)
    elif option == 'category':
        cursor.execute('''SELECT * FROM categories''')
        categories = cursor.fetchall()
        kb = types.InlineKeyboardMarkup(row_width=1)
        for id, name in categories:
            btn = types.InlineKeyboardButton(text=name, callback_data=f'change_product_category_{product}_{id}')
            kb.add(btn)
        bot.edit_message_text(text='Выберите новую категорию', chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=kb)
    else:
        sent = bot.send_message(callback.message.chat.id, 'Введите новое значение')
        bot.register_next_step_handler(sent, change_prod_option_final, option, product, main_message_id)


def change_prod_option_final(message, option, product, main_message_id):
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message.id - 1)
    if option == 'discount':
        cursor.execute(f'''SELECT price FROM products WHERE id = {product}''')
        price = cursor.fetchone()[0]
        price_max_disсount = int(price * ((100 - int(message.text))/100))
        print(price)
        print(price_max_disсount)
        print(product)
        cursor.execute(f'''UPDATE products 
        SET 'priceMaxDiscount' = {price_max_disсount} 
        WHERE id = {product}''')
        db.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(kb_admin.admin_return_btn)
        bot.edit_message_text(text=f'Параметр {option} успешно изменен!', chat_id=message.chat.id, message_id=main_message_id,
        reply_markup=kb)
    elif option == 'price': 
        price = int(message.text)
        cursor.execute(f'''UPDATE products SET price = {price} WHERE id = {product}''')
        db.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(kb_admin.admin_return_btn)
        bot.edit_message_text(text=f'Параметр {option} успешно изменен!', chat_id=message.chat.id, message_id=main_message_id,
        reply_markup=kb)
    else:
        cursor.execute(f'''UPDATE products SET {option} = "{message.text}" WHERE id = {product}''')
        db.commit()
        kb = types.InlineKeyboardMarkup()
        kb.add(kb_admin.admin_return_btn)
        bot.edit_message_text(text=f'Параметр {option} успешно изменен!', chat_id=message.chat.id, message_id=main_message_id,
        reply_markup=kb)


def change_product_category(callback):
    product = int(callback.data.split('_')[-2])
    category = int(callback.data.split('_')[-1])
    cursor.execute(f'''UPDATE products SET category = {category} WHERE id = {product}''')
    db.commit()
    kb = types.InlineKeyboardMarkup()
    kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Категория успешно изменена!', chat_id=callback.message.chat.id, message_id=callback.message.id,
    reply_markup=kb)


def bot_register_categories_handlers():
    bot.register_callback_query_handler(register_category_request, func=lambda callback: callback.data == 'register_new_category')
    bot.register_callback_query_handler(display_categories, func=lambda callback: callback.data == 'send_catalog')
    bot.register_callback_query_handler(display_products, func=lambda callback: 'choose_category_' in callback.data)
    bot.register_callback_query_handler(back_to, func=lambda callback: 'return_to_' in callback.data)
    bot.register_callback_query_handler(display_product_info, func=lambda callback: 'choose_product_' in callback.data)
    bot.register_callback_query_handler(add_to_shop_basket, func=lambda callback: 'add_to_basket_' in callback.data)
    bot.register_callback_query_handler(display_shop_basket, func=lambda callback: callback.data == 'view_shop_basket')
    bot.register_callback_query_handler(delete_product_from_basket, func=lambda callback: 'basket_product_delete_' in callback.data)
    bot.register_callback_query_handler(delete_all_products_from_basket, func=lambda callback: callback.data == 'delete_all_products_from_basket')
    bot.register_callback_query_handler(delete_category_request, func=lambda callback: callback.data == 'delete_category')
    bot.register_callback_query_handler(delete_category, func=lambda callback: 'delete_cat_by_' in callback.data)
    bot.register_callback_query_handler(add_product_to_category, func=lambda callback: callback.data == 'register_new_product')
    bot.register_callback_query_handler(add_product_to_category_final, func=lambda callback: 'add_new_prod_to_' in callback.data)
    bot.register_callback_query_handler(cancel_product, func=lambda callback: 'cancel_adding_prod_' in callback.data)
    bot.register_callback_query_handler(choose_delete_product_category, func=lambda callback: callback.data == 'delete_product')
    bot.register_callback_query_handler(delete_product_from_category, func=lambda callback: 'go_to_product_category_' in callback.data)
    bot.register_callback_query_handler(delete_product_from_category_final, func=lambda callback: 'delete_product_by_id_' in callback.data)
    bot.register_callback_query_handler(change_prod_info_category, func=lambda callback: callback.data == 'change_product_info')
    bot.register_callback_query_handler(change_prod_info_product, func=lambda callback: 'change_prod_info_by_category_' in callback.data)
    bot.register_callback_query_handler(choose_prod_option_request, func=lambda callback: 'change_prod_info_by_prod_' in callback.data)
    bot.register_callback_query_handler(change_prod_option, func=lambda callback: 'change%prod%' in callback.data)
    bot.register_callback_query_handler(change_product_category, func=lambda callback: 'change_product_category_' in callback.data)
