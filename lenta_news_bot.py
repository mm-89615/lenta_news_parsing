import os
import time
from datetime import datetime
from dotenv import load_dotenv

import json
import telebot
from telebot import types, util

from lenta_paser import get_news

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))
bot.delete_webhook()

categories_dict = {
    'Все рубрики': None,
    'Россия': 'russia',
    'Мир': 'world',
    'Бывший СССР': 'ussr',
    'Экономика': 'economics',
    'Силовые структуры': 'forces',
    'Наука и техника': 'science',
    'Спорт': 'sport',
    'Культура': 'culture',
    'Интернет и СМИ': 'media',
    'Ценности': 'style',
    'Путешествия': 'travel',
    'Из жизни': 'life',
    'Среда обитания': 'realty',
    'Забота о себе': 'wellness',
}

news_date = {}


@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(message.chat.id, """
Данный бот собирает новости с сайта новостей <b>LENTA.ru</b>.  
Введите желаемую дату в формате <u><b>YYYY-MM-DD</b></u>.
Ранее <u><b>2001-01-01</b></u> архив новостей отсутствует.  
Далее выберите желаемую категорию из появившегося меню.  
Бот выведет все новости по данной категории в этот день.  
<b>Категория <u>'Все рубрики'</u> может занять больше времени.</b>  """,
                     parse_mode='HTML')


@bot.message_handler(commands=['start'])
def date_message(message):
    bot.send_message(message.chat.id,
                     "<b>Введите дату в формате <u>(YYYY-MM-DD)</u>,</b> "
                     "<b>от <u>2001-01-01</u></b>",
                     parse_mode='HTML')
    bot.register_next_step_handler(message, get_date)


def get_date(message):
    try:
        present_date = datetime.now()
        min_date = datetime(2001, 1, 1)
        year, month, day = message.text.split('-')
        news_date['Дата'] = f'{year}-{month.zfill(2)}-{day.zfill(2)}'
        datetime.strptime(news_date['Дата'], '%Y-%m-%d')
        entered_date = datetime(int(year), int(month), int(day))
        if present_date >= entered_date >= min_date:
            count_message(message)
        else:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id,
                         '<b><u>Введена некорректная дата!</u></b>',
                         parse_mode='HTML')
        date_message(message)


def count_message(message):
    bot.send_message(message.chat.id, """
<b>Введите сколько новостей отобразить.
Напишите желаемое <u>число</u>, либо напишите <u>'Все'</u>, чтобы показать все новости</b>
    """,
                     parse_mode='HTML')
    bot.register_next_step_handler(message, get_count)


def get_count(message):
    try:
        if message.text.lower() == 'все':
            news_date['Количество'] = 'Все'
            category_message(message)
        elif int(message.text):
            news_date['Количество'] = abs(int(message.text))
            category_message(message)
        else:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id,
                         '<b><u>Введено некорректное значение!</u></b>',
                         parse_mode='HTML')
        count_message(message)


def category_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*categories_dict.keys())
    bot.send_message(message.chat.id,"""
<b>Выберите категорию в появившемся меню.
Категория <u>'Все рубрики'</u> может занять больше времени на сбор новостей!</b>""",
                     reply_markup=keyboard,
                     parse_mode='HTML')
    bot.register_next_step_handler(message, get_category)


def get_category(message):
    try:
        if message.text in categories_dict.keys():
            news_date['Категория'] = message.text
            bot.send_message(message.chat.id,
                             '<b>Собираем новости, ожидайте...</b>',
                             parse_mode='HTML')
            return_news(message)
        else:
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id,
                         '<b><u>Такой категории нет!</u></b>',
                         parse_mode='HTML')
        category_message(message)


def return_news(message):
    try:
        get_news(news_date['Дата'], news_date['Категория'])
        with open(f'received_news.json', encoding='UTF-8') as file:
            data = json.load(file)
        if news_date['Количество'] == 'Все' or (
                news_date['Количество'] > len(data)):
            news_date['Количество'] = len(data)
        for index, item in enumerate(
                list(data)[len(data) - news_date['Количество']:len(data)]):
            news = (f"""
<a href='{item.get('url')}'><b>{item.get('title')}</b></a>
<b>Категория</b>:  {item.get('category')}
<b>Дата публикации</b>:  {item.get('publication_time')}
""")
            if index % 20 == 0:
                time.sleep(3)
            bot.send_message(message.from_user.id, news, parse_mode='HTML',
                             disable_web_page_preview=True)
    except Exception:
        bot.send_message(message.from_user.id, 'Новостей этой категории нет.')


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
