from config import db, cursor, bot
from handlers import main

def register_user_info(message):
    cursor.execute(f'''SELECT user_id FROM users WHERE user_id = {message.from_user.id}''')
    user_id = cursor.fetchone()
    
    cursor.execute(f'''INSERT INTO users(user_id, username, first_name, last_name, chat_id) 
VALUES({message.from_user.id}, '{message.from_user.username}', 
'{message.from_user.first_name}', '{message.from_user.last_name}', {message.chat.id});''')
    db.commit()


def check_user_info(message):
    cursor.execute(f'''SELECT user_id, first_name, last_name, username FROM users WHERE user_id = {message.from_user.id}''')
    user_data = cursor.fetchone()
    if user_data is None:
        register_user_info(message)
    else:
        if user_data[1] != message.from_user.first_name or user_data[2] != message.from_user.last_name or user_data[3] != message.from_user.username:
            update_user_info(message)
        cursor.execute(f'''SELECT admin_id FROM admin WHERE admin_id = {user_data[0]}''')
        admin_id = cursor.fetchone()
        if admin_id is not None:
            cursor.execute(f'''UPDATE admin
            SET
            admin_name = '{message.from_user.username}'
            WHERE admin_id = {admin_id[0]}''')
            db.commit()


def update_user_info(message):
    cursor.execute(f'''UPDATE users 
    SET 
    first_name = '{message.from_user.first_name}',
    last_name = '{message.from_user.last_name}',
    username = '{message.from_user.username}'
    WHERE user_id = {message.from_user.id}''')
    db.commit()


def add_to_basket(callback):
    pass

