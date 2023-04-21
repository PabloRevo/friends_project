"""
Файл содержащий Token бота и данные для подключения к БД
"""

import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Файл .env отсутствует')
else:
    load_dotenv()


"""Токен бота"""
TOKEN = os.environ.get('TOKEN')

"""База данных"""
DATABASE = os.environ.get('DATABASE')
USER = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')
HOST = os.environ.get('HOST')
PORT = os.environ.get('PORT')

"""Эквайринг"""
PAY_TOKEN = os.environ.get('PAY_TOKEN')
