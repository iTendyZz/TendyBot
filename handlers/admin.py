from config import bot, cursor, db
from keyboards import main as kb_main
from telebot import types
from keyboards import admin as kb_admin
from db import admin as db_admin

def admin_panel(callback):
    cursor.execute(f'''SELECT users.username, admin.level FROM users
    INNER JOIN admin ON users.user_id = admin.admin_id 
    WHERE user_id = {callback.from_user.id}''')
    info = cursor.fetchone()
    bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=f'''@{info[0]}/lvl:{info[1]}
Вот твоя админская панель:''', 
    reply_markup=kb_admin.admin_menu_keyboard)


def print_admin_list(callback):
    cursor.execute('''SELECT admin.admin_id, users.username
     FROM admin
     INNER join users ON admin.admin_id = users.user_id''')
    admins_data = cursor.fetchall()
    cursor.execute(f'''SELECT level FROM admin WHERE admin_id = {callback.from_user.id}''')
    admin_level = cursor.fetchone()[0]
    admin_list_kb = types.InlineKeyboardMarkup(row_width=1)
    if admin_level == 3:
        for admin_id, admin_username in admins_data:
            admin_list_btn = types.InlineKeyboardButton(text=admin_username, callback_data=f'check_admin_{admin_id}')
            admin_list_kb.add(admin_list_btn)
        admin_list_kb.add(kb_admin.admin_return_btn)
        bot.edit_message_text(text='Вот список наших администраторов:', chat_id=callback.message.chat.id, message_id=callback.message.id, 
        reply_markup=admin_list_kb)
    else:
        admins = 'Вот список наших админов: \n'
        for admin_id, admin_username in admins_data:
            admins += f"<a href='https://t.me/{admin_username}'>{admin_username}</a> \n"
        admin_list_kb.add(kb_admin.admin_return_btn)
        bot.edit_message_text(text=admins, chat_id=callback.message.chat.id, message_id=callback.message.id, 
        reply_markup=admin_list_kb, parse_mode='html', disable_web_page_preview=True)


def check_admin_by_id(callback):
    admin_id = int(callback.data.split('_')[-1])
    cursor.execute(f'''SELECT admin.admin_id, admin.level, users.username, users.first_name, users.last_name 
    FROM admin
    INNER join users ON admin.admin_id = users.user_id 
    WHERE admin.admin_id = {admin_id}''')
    admin_data = cursor.fetchone()

    admin_check_kb = types.InlineKeyboardMarkup(row_width=1)
    admin_btn2 = types.InlineKeyboardButton(text='Удалить администратора', callback_data=f'delete_admin_by_id_{admin_data[0]}')
    admin_btn4 = types.InlineKeyboardButton(text='Поменять уровень полномочий', callback_data=f'change_admin_level_request_{admin_data[0]}')
    admin_check_kb.add(admin_btn2, admin_btn4, kb_admin.admin_return_btn)


    bot.edit_message_text(text=f'''<u>ID</u>: {admin_data[0]}
<u>Имя</u>: {admin_data[3]} {admin_data[4]}
<u>Никнейм</u>: {admin_data[2]}
<u>Уровень полномочий</u>: {admin_data[1]}''', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=admin_check_kb, parse_mode='html')


def change_admin_level_request(callback):
    admin_id = int(callback.data.split('_')[-1])
    cursor.execute(f'''SELECT admin.admin_id, admin.level, users.username, users.first_name, users.last_name 
    FROM admin
    INNER join users ON admin.admin_id = users.user_id 
    WHERE admin.admin_id = {admin_id}''')
    admin_data = cursor.fetchone()

    admin_change_lvl_kb = types.InlineKeyboardMarkup()
    admin_change_lvl_btn1 = types.InlineKeyboardButton(text='1', callback_data=f'change_admin_level_{admin_data[0]}_to_1')
    admin_change_lvl_btn2 = types.InlineKeyboardButton(text='2', callback_data=f'change_admin_level_{admin_data[0]}_to_2')
    admin_change_lvl_btn3 = types.InlineKeyboardButton(text='3', callback_data=f'change_admin_level_{admin_data[0]}_to_3')
    admin_change_lvl_cancel_btn = types.InlineKeyboardButton(text='Отмена', callback_data=f'check_admin_{admin_data[0]}')
    if admin_data[1] == 1:
        admin_change_lvl_kb.add(admin_change_lvl_btn2, admin_change_lvl_btn3)
    elif admin_data[1] == 2:
        admin_change_lvl_kb.add(admin_change_lvl_btn1, admin_change_lvl_btn3)
    elif admin_data[1] == 3:
        admin_change_lvl_kb.add(admin_change_lvl_btn1, admin_change_lvl_btn2)
    admin_change_lvl_kb.row(admin_change_lvl_cancel_btn)

    bot.edit_message_text(text=f'''<u>ID</u>: {admin_data[0]}
<u>Имя</u>: {admin_data[3]} {admin_data[4]}
<u>Никнейм</u>: {admin_data[2]}
<u>Уровень полномочий</u>: {admin_data[1]}''', chat_id=callback.message.chat.id, message_id=callback.message.id, 
    reply_markup=admin_change_lvl_kb, parse_mode='html')        


def change_admin_level(callback):
    admin_id = int(callback.data.split('_')[3])
    admin_level = int(callback.data.split('_')[-1])
    cursor.execute(f'''UPDATE admin SET level = {admin_level} WHERE admin_id = {admin_id}''')
    db.commit()
    back_kb = types.InlineKeyboardMarkup()
    back_kb.add(kb_admin.admin_return_btn)
    bot.edit_message_text(text='Уровень успешно изменен!', chat_id=callback.message.chat.id, message_id=callback.message.id, reply_markup=back_kb)

def step_to(callback):
    step = callback.data.split('_')[-2]
    if step == 'admin':
        admin_settings(callback)
    if step == 'cp':
        cp_settings(callback)


def add_new_admin_request(callback):
    add_admin_kb = types.InlineKeyboardMarkup()
    add_admin_kb.add(kb_admin.admin_return_btn)

    sent = bot.edit_message_text(text='Введите ID пользователя:', chat_id=callback.message.chat.id, 
    message_id=callback.message.id, reply_markup=add_admin_kb)
    bot.register_next_step_handler(sent, add_new_admin)


def add_new_admin(message):
    user_id = int(message.text)
    bot.delete_message(message.chat.id, message.id)
    db_admin.add_new_admin(user_id)
    adm_back_kb = types.InlineKeyboardMarkup()
    adm_back_kb.add(kb_admin.admin_return_btn)

    bot.send_message(message.chat.id, 'Новый администратор успешно добавлен!', reply_markup=adm_back_kb)

def cp_settings(callback):
    bot.edit_message_text(text='Вот доступные настройки категорий и продуктов:', chat_id=callback.message.chat.id, 
    message_id=callback.message.id, reply_markup=kb_main.cat_and_prod_kb)


def admin_settings(callback):
    admin_kb = types.InlineKeyboardMarkup(row_width=1)
    admin_btn1 = types.InlineKeyboardButton(text='Добавить администратора', callback_data='add_new_admin_by_id')
    admin_btn3 = types.InlineKeyboardButton(text='Список администраторов', callback_data='print_admin_list')
    admin_return_btn = types.InlineKeyboardButton(text='Назад', callback_data='back_to_AdminPanel')
    cursor.execute(f'''SELECT level FROM admin WHERE admin_id = {callback.from_user.id}''')
    adm_lvl = cursor.fetchone()[0]
    if adm_lvl == 3: admin_kb.add(admin_btn1, admin_btn3, admin_return_btn)
    if adm_lvl < 3: admin_kb.add(admin_btn3, admin_return_btn)

    bot.edit_message_text(text='Настройки администраторских полномочий:', chat_id=callback.message.chat.id, 
    message_id=callback.message.id, reply_markup=admin_kb)


def register_admin_handlers():
    bot.register_callback_query_handler(admin_panel, func=lambda callback: callback.data == 'show_admin_panel')
    bot.register_callback_query_handler(step_to, func=lambda callback: 'step_to_' in callback.data)
    bot.register_callback_query_handler(print_admin_list, func=lambda callback: callback.data == 'print_admin_list')
    bot.register_callback_query_handler(check_admin_by_id, func=lambda callback: 'check_admin_' in callback.data)
    bot.register_callback_query_handler(change_admin_level_request, func=lambda callback: 'change_admin_level_request_' in callback.data)
    bot.register_callback_query_handler(add_new_admin_request, func=lambda callback: callback.data == 'add_new_admin_by_id')
    bot.register_callback_query_handler(change_admin_level, func=lambda callback: 'change_admin_level_' in callback.data)
