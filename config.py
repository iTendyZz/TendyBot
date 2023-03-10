import telebot
import sqlite3
import psycopg2

bot = telebot.TeleBot('5835811151:AAEoKR2NHsFjhYaZ8EpLqKjEr39FrAbwUxw')

admin_chat = -804874780

db = psycopg2.connect(database='TendyShopDB', 
user='itendy',
password='4eByPeKu',
host='localhost',
port='5432')
cursor = db.cursor()


