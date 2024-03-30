import os
import time
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

import json
import telebot
from telebot import types

from lenta_paser import get_news
from bot_cmds_list import private

load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

categories = {
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

# словарь в который собирается пользовательский ввод
# категория, количество новостей, дата
news_date = {}
# получение сегодняшней и вчерашней даты
today = date.today()
yesterday = today - timedelta(days=1)


@bot.message_handler(commands=['about'])
def about(message):
    """ Вывод команды /about в чате"""
    bot.send_message(
        message.chat.id,
        "Данный бот собирает новости с сайта новостей <b>LENTA.ru</b>.\n"
        "Введите желаемую дату в формате <u><b>YYYY-MM-DD</b></u>, "
        "либо выберите из предложенных вариантов.\n"
        "Ранее <u><b>2001-01-01</b></u> архив новостей отсутствует.\n"
        "Введите желаемое количество новостей, которое нужно отобразить, либо "
        "выберите в появившемся меню.\n"
        "Далее, выберите желаемую категорию из появившегося меню.\n"
        "Бот выведет все новости по данной категории в этот день.\n"
        "<b>Категория <u>'Все рубрики'</u> может занять больше времени.</b>",
        parse_mode='HTML')


@bot.message_handler(commands=['cancel'], regexp='отмена')
def start_message(message):
    """ Отмена ввода данных и очистка словаря"""
    news_date.clear()
    bot.send_message(
        message.chat.id,
        "<b>Введите /start для поиска новостей.</b>\n"
        "<b>Введите /about для получения информации о боте.</b>",
        parse_mode='HTML')


@bot.message_handler(commands=['start'])
def date_message(message):
    """ Считывает введенную в чате дату от пользователя """
    news_date.clear()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton(f'{today}')
    btn2 = types.KeyboardButton(f'{yesterday}')
    kb.add(btn1, btn2)
    bot.send_message(
        message.chat.id,
        "<b>Введите дату в формате <u>(YYYY-MM-DD)</u>,</b> "
        "<b>от <u>2001-01-01</u>, либо выберите вариант из меню.</b>",
        reply_markup=kb,
        parse_mode='HTML')
    bot.register_next_step_handler(message, get_date)


def get_date(message):
    """ Обрабатывает полученную дату или реагирует на другие действия"""
    # обработка команд 'отмена' и '/start'
    if message.text.lower() == 'отмена' or message.text == '/cancel':
        start_message(message)
    elif message.text == '/start':
        date_message(message)
    elif message.text == '/about':
        about(message)
    else:
        try:
            # Обработка даты, чтоб была в формате YYYY-MM-DD, а также
            # находилась в не раньше 2001-01-01 и не позже, чем сегодня
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
            # повторный запрос ввода даты, если некорректная дата
            bot.send_message(
                message.chat.id,
                '<b><u>Введена некорректная дата!</u></b>',
                parse_mode='HTML')
            date_message(message)


def count_message(message):
    """ Считывает введенное количество новостей в чате"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('25')
    btn2 = types.KeyboardButton('50')
    btn3 = types.KeyboardButton('75')
    btn4 = types.KeyboardButton('100')
    btn5 = types.KeyboardButton('Все')
    kb.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(
        message.chat.id,
        "<b>Введите сколько новостей отобразить.</b>\n"
        "<b>Напишите желаемое <u>число</u>, либо напишите <u>'Все'</u>,</b> "
        "<b>чтобы показать все новости.</b>\n"
        "<b>Также можно выбрать один из предложенных вариантов.</b>",
        reply_markup=kb,
        parse_mode='HTML')
    bot.register_next_step_handler(message, get_count)


def get_count(message):
    """ Обработка полученного количества и различных команд"""
    # обработка команд 'отмена' и '/start'
    if message.text.lower() == 'отмена' or message.text == '/cancel':
        start_message(message)
    elif message.text == '/start':
        date_message(message)
    elif message.text == '/about':
        about(message)
    else:
        try:
            # Проверка корректности ввода числа, либо что введено 'все'
            if message.text.lower() == 'все':
                news_date['Количество'] = 'Все'
                category_message(message)
            elif int(message.text):
                news_date['Количество'] = abs(int(message.text))
                category_message(message)
            else:
                raise ValueError
        except ValueError:
            # повторный запрос ввода количества, если некорректное значение
            bot.send_message(
                message.chat.id,
                "<b><u>Введено некорректное значение!</u></b>",
                parse_mode='HTML')
            count_message(message)


def category_message(message):
    """ Считывание в чате введенной категории """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*categories.keys())
    bot.send_message(
        message.chat.id,
        "<b>Выберите категорию в появившемся меню.</b>\n"
        "<b>Категория <u>'Все рубрики'</u></b> "
        "<b>может занять больше времени на сбор новостей!</b>",
        reply_markup=keyboard,
        parse_mode='HTML')
    bot.register_next_step_handler(message, get_category)


def get_category(message):
    """ Обработка полученной категории и других действий"""
    # обработка команд 'отмена' и '/start'
    if message.text.lower() == 'отмена' or message.text == '/cancel':
        start_message(message)
    elif message.text == '/start':
        date_message(message)
    elif message.text == '/about':
        about(message)
    else:
        try:
            # Проверка наличия введенной категории в словаре категорий
            if message.text in categories.keys():
                news_date['Категория'] = message.text
                bot.send_message(message.chat.id,
                                 '<b>Собираем новости, ожидайте...</b>',
                                 parse_mode='HTML')
                return_news(message)
            else:
                raise ValueError
        except ValueError:
            # повторный запрос ввода категории в случае ошибки
            bot.send_message(message.chat.id,
                             '<b><u>Такой категории нет!</u></b>',
                             parse_mode='HTML')
            category_message(message)


def return_news(message):
    """ Обрабатывает результат полученных данных от пользователя и
    вывод все новости в чате. """
    try:
        # Попытка запустить парсер новостей
        get_news(news_date['Дата'], news_date['Категория'],
                 message.from_user.id)
        # Проверка, что новости данной категории есть, иначе не будет
        # создан json файл с новостями
        if os.path.exists(f'received_news/{message.from_user.id}.json'):
            with open(f'received_news/{message.from_user.id}.json',
                      encoding='UTF-8') as file:
                data = json.load(file)
        else:
            # Вызывает ошибку, если отсутствует файл (новостей нет)
            raise ValueError
        # сохранение количества в переменную, чтобы не перезаписать
        # введенное количество на случай повторного запроса других категорий
        count_ = news_date['Количество']
        # обработка количества, чтоб не было больше, чем есть новостей
        if news_date['Количество'] == 'Все' or (
                news_date['Количество'] > len(data)):
            count_ = len(data)
        # вывод в чат новостей
        for index, item in enumerate(
                list(data)[len(data) - count_:len(data)]):
            news = (f"""
<a href='{item.get('url')}'><b>{item.get('title')}</b></a>
<b>Категория</b>:  {item.get('category')}
<b>Дата публикации</b>:  {item.get('publication_time')}
""")
            # остановка каждый 3 секунды (антиспам)
            if index % 20 == 0:
                time.sleep(3)
            bot.send_message(message.from_user.id, news, parse_mode='HTML',
                             disable_web_page_preview=True)
        # предложение выбора новой категории, после вывода всех новостей
        bot.send_message(message.from_user.id,
                         '<b>Новостей этой категории больше нет.</b>',
                         parse_mode='HTML')
        category_message(message)
    except ValueError:
        # выбор новой категории в случай отсутствия новостей по категории
        bot.send_message(message.from_user.id,
                         '<b>Новостей этой категории нет.</b>',
                         parse_mode='HTML')
        category_message(message)


def main():
    bot.delete_webhook(drop_pending_updates=True)
    bot.set_my_commands(commands=private,
                        scope=types.BotCommandScopeAllPrivateChats())
    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()
