import json
import telebot
import logging
from pyarr import RadarrAPI
from myradarr import *


def check_allowed_usernames(username):
    return username in allowed_usernames


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

# get allowed usernames from settings file
allowed_usernames = settings['allowed_usernames']

# get config for radarr
radarr_host_url = settings['radarr_host_url']
radarr_api_key = settings['radarr_api_key']

# Instantiate RadarrAPI
radarr = RadarrAPI(radarr_host_url, radarr_api_key)

@bot.message_handler(commands=['start'])
def start(message):
    if not check_allowed_usernames(message.from_user.username):
        bot.send_message(message.from_user.id, "К сожалению у вас нет доступа к боту")
        return
    logger.debug(f'Received start from "{message.from_user.username}"')
    bot.send_message(message.from_user.id, "👋 Привет! Я скачаю за тебя фильмы и сериалы с торрентов, просто пиши мне название фильма")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if not check_allowed_usernames(message.from_user.username):
        bot.send_message(message.from_user.id, "К сожалению у вас нет доступа к боту")
        return
    logger.debug(f'Received message from "{message.from_user.username}"')
    movies = find_movies(radarr, message.text)

    if len(movies) == 0:
        bot.send_message(message.from_user.id, "К сожалению я ничего не нашел(")
        return

    # TODO: Вытащить в конфиг
    max_messages = 5

    if len(movies) >= max_messages:
        bot.send_message(message.from_user.id, f"Нашел {len(movies)} фильмов, но покажу только {max_messages}")

    for m in movies:
        if max_messages == 0:
            break

        # Markup for download button
        kb = telebot.types.InlineKeyboardMarkup(row_width=1)
        btn_types = telebot.types.InlineKeyboardButton(text='Скачать', callback_data=str(m['tmdbId']))
        kb.add(btn_types)

        bot.send_photo(message.from_user.id, photo=m['image_url'], caption=m['title'], reply_markup=kb)
        bot.send_message(message.from_user.id, f"{m['overview']}\n")
        bot.send_message(message.from_user.id, f"{m['scores']}")

        max_messages -= 1


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    # TODO: make root_dir and quality_profile_selection
    # radarr.get_quality_profile()
    # radarr.get_root_folder()

    # Get first root folder as default
    root_dir = radarr.get_root_folder()[0]["path"]

    # Set Ultra-HD profile as default
    quality_profile_id = 5

    movie = radarr.lookup_movie(term=f'tmdb:{call.data}')[0]
    radarr.add_movie(movie, root_dir=root_dir, quality_profile_id=quality_profile_id)
    bot.answer_callback_query(call.id, "Поставил на закачку")


logger.info('Starting polling...')
bot.infinity_polling()
logger.info('Exiting')