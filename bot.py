from config import bot
from colorama import Fore
from handlers import main as hand_main
from handlers import categories
from db import create_db
from db import main as db_main
from handlers import admin
from handlers import buy_system

# Register handlers in main file

hand_main.bot_register_main_handlers()
categories.bot_register_categories_handlers()
admin.register_admin_handlers()
buy_system.bot_register_buy_system_handlers()

# Creating tables in db.db
create_db.create_tables()

# Starting bot with cool text
print(Fore.GREEN + '[INFO] BOT IS ACTIVE' + Fore.RESET + '')
bot.infinity_polling()
print(Fore.RED + '[INFO] BOT IS OFFLINE' + Fore.RESET + '')

