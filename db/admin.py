from config import db, cursor, bot

def add_new_admin(user_id):
    cursor.execute(f'''SELECT username FROM users WHERE user_id = {user_id}''')
    username = cursor.fetchone()[0]

    cursor.execute(f'''INSERT INTO admin(admin_id, admin_name, level) VALUES({user_id}, '{username}', 1)''')
    db.commit()

