from datetime import date, datetime
from glob import glob
import logging
from random import choice
import re

import ephem

from utils import check_city, check_planet, convert_to_calc, get_smile, main_keyboard, play_random_numbers

# Функция для приветствия пользователя
def greet_user(update, context):
    logging.info('Bot has been lauched')
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(
        f'Дороу, жабокрад {context.user_data["emoji"]}!',
        reply_markup = main_keyboard()
    )

# Функция для ответа пользователю его же сообщением
def talk_to_me(update, context):
    user_text = update.message.text
    logging.info(f'User said {user_text}')
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(f'{user_text} {context.user_data["emoji"]}', reply_markup = main_keyboard())

# Функция нахождения текущего созвездия объекта
def find_constellation(update, context):
    planet = update.message.text.split()[-1].lower().capitalize()
    if not check_planet(planet):
        update.message.reply_text('Сори, жабокрад, такой планеты не видел', reply_markup = main_keyboard())
        return
    today = date.today()
    logging.info(f'User asked for a constellation of {planet} for {today}')
    planet_function = getattr(ephem, planet, None)
    if planet_function is not None:
        print(planet_function)
        planet_data = planet_function(today)
        print(planet_data)
        update.message.reply_text(f'Сейчас планета {planet} находится в созвездии {ephem.constellation(planet_data)[-1]}', reply_markup = main_keyboard())
        print(ephem.constellation(planet_data))
    else:
        update.message.reply_text('Сори, жабокрад, такой планеты не знаю', reply_markup = main_keyboard())

#Функция подсчета слов в предложении
def count_words(update, context):
    sentence = update.message.text
    sentence = sentence.replace('-',' ')
    sentence = re.split(r"[^ёЁА-яa-zA-Z0-9-]", sentence)
    sentence = [x for x in sentence if x != '']
    sentence.remove('wordcount')
    update.message.reply_text(f'Количество слов в предложении: {len(sentence)}', reply_markup = main_keyboard())

#Нахождение следующего полнолуния
def next_full_moon(update, context):
    date_string = update.message.text.split()[-1]
    try:
        user_date = datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        update.message.reply_text(f'Дата должна быть в формате ГГГГ-ММ-ДД', reply_markup = main_keyboard())
    update.message.reply_text(f'Дата ближайшего полнолуния: {ephem.next_full_moon(user_date)}', reply_markup = main_keyboard())

#Функция случаного числа
def guess_number(update, context):
    print(context.args)
    if context.args:
        try:
            user_number = int(context.args[0])
            message = play_random_numbers(user_number)
        except (TypeError, ValueError):
            message = 'Введите целое число'
    else:
        message = 'Введите целое число'
    update.message.reply_text(message, reply_markup = main_keyboard())

#функция отправки картинки жабы
def send_toad_picture(update, context):
    toad_photos_list = glob('images\\toad*.jp*g')
    toad_pic_filename = choice(toad_photos_list)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id = chat_id, photo = open(toad_pic_filename, 'rb'), reply_markup = main_keyboard())

#Функция для игры в города
def play_cities(update, context):
    if context.args:
        user_city = " ".join(context.args).lower()
        message = check_city(user_city,context.user_data)
        update.message.reply_text(message, reply_markup = main_keyboard())
    else:
        message = 'Введите город'
        update.message.reply_text(message, reply_markup = main_keyboard())

#Функция общения с калькулятором
def talk_to_calculate(update, context):
    if context.args:
        user_text = "".join(context.args)
        result = convert_to_calc(user_text)
        update.message.reply_text(result, reply_markup = main_keyboard())
    else:
        message = 'Введите выражение после команды'
        update.message.reply_text(message, reply_markup = main_keyboard())

#Функция возврата координат
def user_coordinates(update, context):
    context.user_data['emoji'] = get_smile(context.user_data)
    coords = update.message.location
    update.message.reply_text(
        f"Ваши координаты {coords} {context.user_data['emoji']}!",
        reply_markup = main_keyboard()
    )