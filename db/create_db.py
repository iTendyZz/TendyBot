from config import db, cursor

def create_tables():
    '''Creates tables in database'''

    # main user info
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        chat_id INT)''')
    db.commit()

    # our categories
    cursor.execute('''CREATE TABLE IF NOT EXISTS categories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL)''')
    db.commit()

    # Our sweet products :D
    cursor.execute('''CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT,
        price INT,
        price_max_disсount INT,
        category INT,
        description TEXT)''')
    db.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INT,
        admin_name TEXT,
        level INT)''')
    db.commit()


    cursor.execute('''CREATE TABLE IF NOT EXISTS shop_basket(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INT,
        product_id INT,
        cost INT)''')
    db.commit()