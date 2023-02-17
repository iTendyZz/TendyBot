from config import bot, db, cursor
from keyboards import main as kb_main
from telebot import types
from db import main as db_main
from db import admin as db_admin
from handlers import admin

def start_message(message):
    '''Sending the start message about a shop'''
    start_kb = types.InlineKeyboardMarkup(row_width=1)
    start_btn1 = types.InlineKeyboardButton(text='Каталог', callback_data='send_catalog')
    start_btn2 = types.InlineKeyboardButton(text='Скидки и акции', callback_data='send_discounts')
    start_btn3 = types.InlineKeyboardButton(text='Обратная связь', callback_data='send_feedback_admin')
    start_kb.add(start_btn1, start_btn2, start_btn3)

    db_main.check_user_info(message)
    cursor.execute(f'''SELECT admin_id, level FROM admin WHERE admin_id = {message.chat.id}''')
    admin_data = cursor.fetchone()
    if admin_data is not None:
        start_admin_btn = types.InlineKeyboardButton(text='Админ панель))', callback_data='show_admin_panel')
        start_kb.add(start_admin_btn)
    cursor.execute(f'''SELECT id FROM shop_basket WHERE user_id = {message.chat.id}''')
    basket = cursor.fetchone()
    if basket is not None:
        basket_btn = types.InlineKeyboardButton(text='Корзина', callback_data='view_shop_basket')
        start_kb.add(basket_btn)
    cursor.execute(f'''SELECT * FROM user_logins WHERE user_id = {message.chat.id}''')
    logins = cursor.fetchall()
    if logins is not None:
        logins_btn = types.InlineKeyboardButton(text='Ваши покупки', callback_data=f'show_buys_{message.chat.id}')
        start_kb.add(logins_btn)
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, f'''Здарова, _{message.chat.first_name}_!
*TendyShop привествует нового клиента!*
Чтобы проверить каталог нажми на кнопочку!''', parse_mode='markdown', reply_markup=start_kb)
    

def show_buys(callback):
    cursor.execute(f'''SELECT login, password, product_name FROM user_logins WHERE user_id = {callback.from_user.id}''')
    logins_info = cursor.fetchall()
    info = ''
    for login, password, product_name in logins_info:
        info += f'{login}:{password} ({product_name})\n'
    bot.edit_message_text(text=f'Ваши покупки:\n{info}', message_id=callback.message.id, chat_id=callback.message.chat.id, reply_markup=kb_main.return_keyboard)


def show_user_chat_id(message):
    bot.delete_message(message.chat.id, message.id)
    
    bot.send_message(message.chat.id, f'{message.chat.id}', reply_markup=kb_main.return_keyboard)

def back_to_message(callback):
    check = callback.data.split('_')[-1]
    if check == 'startMessage':
        start_message(callback.message)
    elif check == 'AdminPanel':
        admin.admin_panel(callback)


def admin_feedback(callback):
    bot.edit_message_text('''Контакты админа:
<a href='https://t.me/+BtgSi1hODgBkYjcy'>Telegram</a>
<a href='https://discord.gg/PJwNJe9XMp'>Discord</a>''', message_id=callback.message.id, chat_id=callback.message.chat.id, parse_mode='html',
 reply_markup=kb_main.return_keyboard)


def bot_register_main_handlers():
    '''Register our handlers'''
    bot.register_message_handler(start_message, commands=['start'])
    bot.register_callback_query_handler(admin_feedback, func=lambda callback: 'send_feedback_' in callback.data)
    bot.register_callback_query_handler(back_to_message, func=lambda callback: 'back_to_' in callback.data)
    bot.register_message_handler(show_user_chat_id, commands=['show_id'])
    bot.register_callback_query_handler(show_buys, func=lambda callback: 'show_buys_' in callback.data)

