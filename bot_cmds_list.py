from telebot.types import BotCommand

private = [
    BotCommand(command='start', description='Начать поиск новостей'),
    BotCommand(command='about', description='Информация о боте'),
    BotCommand(command='cancel', description='Отменить введенные данные')
]