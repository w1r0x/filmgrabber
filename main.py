import json
import telebot
import logging

logger = logging.getLogger(__name__)
log_levels = {'info': logging.INFO, 'debug': logging.DEBUG}

with open('settings.json', 'r') as file:
    settings = json.load(file)

# set telegram bot api key
tg_bot_api_key = settings['tg_bot_api_key']

# set log level from settings file
log_level = log_levels[settings['log_level']]
logging.basicConfig(level=log_level)
bot = telebot.TeleBot(tg_bot_api_key)


@bot.message_handler(commands=['start'])
def start(message):
    logger.debug(f'Received start from "{message.from_user.username}"')
    bot.send_message(message.from_user.id, "👋 Привет! Я скачаю за тебя фильмы и сериалы с торрентов")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    logger.debug(f'Received message from "{message.from_user.username}"')
    bot.send_message(message.from_user.id, 'Пока я ничего не умею, но скоро научусь')


logger.info('Starting polling...')
bot.infinity_polling()
logger.info('Exiting')