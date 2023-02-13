import telebot
import sqlite3

bot = telebot.TeleBot('5835811151:AAEoKR2NHsFjhYaZ8EpLqKjEr39FrAbwUxw')

admin_chat = -804874780

db = sqlite3.connect('db.db', check_same_thread=False)
cursor = db.cursor()
