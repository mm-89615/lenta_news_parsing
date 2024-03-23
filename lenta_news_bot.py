import os
import time
from dotenv import load_dotenv

import json
import telebot
from telebot import types

from main import get_news

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

categories = ['Все рубрики', 'Россия', 'Мир', 'Бывший СССР', 'Экономика',
              'Силовые структуры', 'Наука и техника',
              'Спорт', 'Культура', 'Интернет и СМИ', 'Ценности',
              'Путешествия', 'Из жизни', 'Среда обитания', 'Забота о себе']

news_date = {}


@bot.message_handler(commands=['start'])
def get_date(message):
    sent_message = bot.send_message(message.chat.id,
                                    "Введите дату в формате (YYYY-MM-DD)")
    bot.register_next_step_handler(sent_message, get_category)


def get_category(message):
    news_date['Дата'] = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*categories)
    bot.send_message(message.chat.id, 'Выберите категорию',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, return_news)


def return_news(message):
    news_date['Категория'] = message.text
    get_news(news_date['Дата'], news_date['Категория'])
    with open(f'news_archive/world-2001-01-01.json', encoding='UTF-8') as file:
        data = json.load(file)
    for index, item in enumerate(data):
        news = f"<a href='{item.get('url')}'>{item.get('title')}.</a> Дата публикации: {item.get('publication_time')}"
        if index % 20 == 0:
            time.sleep(3)
        bot.send_message(message.chat.id, news, parse_mode='HTML',
                         disable_web_page_preview=True)


bot.polling(none_stop=True)
