from datetime import date, datetime
from glob import glob
import logging
from random import randint, choice
import re

from emoji import emojize
import ephem
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

# Создаем функцию для приветствия пользователя
def greet_user(update, context):
    logging.info('Bot has been lauched')
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(f'Дороу, жабокрад {context.user_data["emoji"]}!')

# Создаем функцию для ответа пользователю его же сообщением
def talk_to_me(update, context):
    user_text = update.message.text
    logging.info(f'User said {user_text}')
    context.user_data['emoji'] = get_smile(context.user_data)
    update.message.reply_text(f'{user_text} {context.user_data["emoji"]}')

# Функция генерирует смайлик
def get_smile(user_data):
    if 'emoji' not in user_data:
        smile = choice(settings.USER_EMOJI)
        return emojize(smile, language='alias')
    return user_data['emoji']

# Проверяет, что объект есть в списке объектов пакета ephem
def check_planet(planet):
    for item in ephem._libastro.builtin_planets():
        if planet in str(item):
            return True
    return False    
    
# Функция нахождения текущего созвездия объекта
def find_constellation(update, context):
    planet = update.message.text.split()[-1].lower().capitalize()
    if not check_planet(planet):
        update.message.reply_text('Сори, жабокрад, такой планеты не видел')
        return
    today = date.today()
    logging.info(f'User asked for a constellation of {planet} for {today}')
    planet_function = getattr(ephem, planet, None)
    if planet_function is not None:
        print(planet_function)
        planet_data = planet_function(today)
        print(planet_data)
        update.message.reply_text(f'Сейчас планета {planet} находится в созвездии {ephem.constellation(planet_data)[-1]}')
        print(ephem.constellation(planet_data))
    else:
        update.message.reply_text('Сори, жабокрад, такой планеты не знаю')

#Функция подсчета слов в предложении
def count_words(update, context):
    sentence = update.message.text
    sentence = sentence.replace('-',' ')
    sentence = re.split(r"[^ёЁА-яa-zA-Z0-9-]", sentence)
    sentence = [x for x in sentence if x != '']
    sentence.remove('wordcount')
    update.message.reply_text(f'Количество слов в предложении: {len(sentence)}')

#Нахождение следующего полнолуния
def next_full_moon(update, context):
    date_string = update.message.text.split()[-1]
    try:
        user_date = datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        update.message.reply_text(f'Дата должна быть в формате ГГГГ-ММ-ДД')
    update.message.reply_text(f'Дата ближайшего полнолуния: {ephem.next_full_moon(user_date)}')

#Игра в случайные числа
def play_random_numbers(user_number):
    bot_number = randint(user_number - 10, user_number +10)
    if user_number > bot_number:
        message = f'Твое число {user_number}, мое - {bot_number}, ты выиграл!'
    elif user_number == bot_number:
        message = f'Твое число {user_number}, мое - {bot_number}, ничья!'
    else:
        message = f'Твое число {user_number}, мое - {bot_number}, я выиграл!'
    return message

#Прием числа от пользователя и вывод сообщения
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
    update.message.reply_text(message)

#функция отправки картинки жабы
def send_toad_picture(update, context):
    toad_photos_list = glob('images\\toad*.jp*g')
    toad_pic_filename = choice(toad_photos_list)
    chat_id = update.effective_chat.id
    context.bot.send_photo(chat_id = chat_id, photo = open(toad_pic_filename, 'rb'))

#Функция для проверки города
def check_city(user_city, user_data):
    #базовые проверки введенного города на первый символ и что не введены символы кроме букв и двух тире/дефисов
    result = re.fullmatch("[ёа-я]*\s?[-‐‑-ꟷー一]?[ёа-я]*\s?[-‐‑-ꟷー一]?[ёа-я]*", user_city)
    if not result:
        return f'Введи город на русском'
    if user_city[0] in ['ы', 'ъ', 'ь']:
        return f'Город не может начинаться с такой буквы'
    #проверяем, играл ли пользователь уже в эту игру, если нет, то записываем для него список городов
    if 'initial_cities' not in user_data:
        if user_city in [x.lower() for x in settings.INITIAL_CITIES]:
            user_data['initial_cities'] = [x.lower() for x in settings.INITIAL_CITIES]
            user_data['passed_cities'] = []
            user_data['current_user_letter'] = user_city[0]
        else:
            return f'Не знаю такого города'
    #тут основная логика
    if  user_city[0] != user_data['current_user_letter']:
        return f'Твой город должен начинаться с буквы {user_data["current_user_letter"].capitalize()}'
    if user_city in user_data['initial_cities']:
        user_data['passed_cities'].append(user_city)
        user_data['initial_cities'].remove(user_city)
        i = 1
        while user_city[-i] in ['ы', 'ъ', 'ь']:
            i += 1
        letter = user_city[-i]
        r = re.compile(f"{letter}[ёа-я]*[-‐‑-ꟷー一]?[ёа-я]*[-‐‑-ꟷー一]?[ёа-я]*")
        try:
            suitable_cities = list(filter(r.match, user_data['initial_cities']))
            bot_city = choice(suitable_cities)
            user_data['passed_cities'].append(bot_city)
            user_data['initial_cities'].remove(bot_city)
            ind = 1
            while bot_city[-ind] in ['ы', 'ъ', 'ь']: 
                ind += 1
            user_data['current_user_letter'] = bot_city[-ind]
            return f'{bot_city.capitalize()}. Твой ход'
        except IndexError:
            return f'Не знаю больше городов на букву {letter.capitalize()}. Ты выиграл'
    elif user_city in user_data['passed_cities']:
        return f'Город {user_city.capitalize()} уже был'
    else:
        return f'Не знаю такого города'
     
#Функция для игры в города
def play_cities(update, context):
    if context.args:
        user_city = " ".join(context.args).lower()
        message = check_city(user_city,context.user_data)
        update.message.reply_text(message)
    else:
        message = 'Введите город'
        update.message.reply_text(message)

#Функция замены запятой на точку и приведения типов
def change_delimeter_and_type(numbers):
    numbers = [item.replace(',', '.') for item in numbers]
    for i, item in enumerate(numbers):
        if '.' in item:
            item = float(item)
            numbers[i] = item
        else:
            item = int(item)
            numbers[i] = item
    return numbers

#Функция вычислений
def calculation(user_string, numbers):
    if '+' in user_string:
        return f'Результат сложения: {numbers[0] + numbers[1]}'
    elif '-' in user_string:
        return f'Результат вычитания: {numbers[0] - numbers[1]}'
    elif '*' in user_string:
        return f'Результат умножения: {numbers[0] * numbers[1]}'
    elif '/' in user_string:
        try:
            division_result = numbers[0]/numbers[1]
            return f'Результат деления: {division_result}'
        except ZeroDivisionError:
            return 'На ноль делить нельзя'

#Функция калькулятора
def convert_to_calc(user_string): 
    result = re.fullmatch("-?[0-9]+[.,]?[0-9]*[-+*/]-?[0-9]+[.,]?[0-9]*", user_string)
    if not result:
        return 'Введи корректное выражение после команды'
    signs = [x for x in user_string if x in '-+*/']
    number_of_signs = len(signs)
    if number_of_signs == 1: #2 positives
        number_list = re.split('[-+*/]',user_string)
        number_list = change_delimeter_and_type(number_list)
        return calculation(user_string, number_list)
    elif number_of_signs == 3:
        if len(set(signs)) == 1: #2 negatives, minus
            number_list = user_string.split('-')
            number_list = [x for x in number_list if x != '']
            number_list = change_delimeter_and_type(number_list)
            number_list = [-x for x in number_list]
            return calculation(user_string, number_list)
        else: #2 negatives, another action
            user_string = user_string.replace('-','')
            number_list = re.split('[+*/]',user_string)
            number_list = change_delimeter_and_type(number_list)
            number_list = [-x for x in number_list]
            return calculation(user_string, number_list)
    elif number_of_signs == 2: #1 negative
        result = re.fullmatch("-[0-9]+[.,]?[0-9]*[-+*/][0-9]+[.,]?[0-9]*", user_string)
        if not result:
            if len(set(signs)) == 1: #Second negative, minus
                number_list = user_string.split('-')
                number_list = [x for x in number_list if x != '']
                number_list = change_delimeter_and_type(number_list)
                number_list[1] = number_list[1] * (-1)
                return calculation(user_string, number_list)
            else: #Second negative, another action
                user_string = user_string.replace('-','')
                number_list = re.split('[+*/]',user_string)
                number_list = change_delimeter_and_type(number_list)
                number_list[1] = number_list[1] * (-1)
                return calculation(user_string, number_list)
        if len(set(signs)) == 1: #First negative, minus
            number_list = user_string.split('-')
            number_list = [x for x in number_list if x != '']
            number_list = change_delimeter_and_type(number_list)
            number_list[0] = number_list[0] * (-1)
            return calculation(user_string, number_list)
        else: #First negative, another action
            user_string = user_string.replace('-','')
            number_list = re.split('[+*/]',user_string)
            number_list = change_delimeter_and_type(number_list)
            number_list[0] = number_list[0] * (-1)
            return calculation(user_string, number_list)
    
#Функция общения с калькулятором
def talk_to_calculate(update, context):
    if context.args:
        user_text = "".join(context.args)
        result = convert_to_calc(user_text)
        update.message.reply_text(result)
    else:
        message = 'Введите выражение после команды'
        update.message.reply_text(message)

# Тело бота
def main():
    # Создаем бота и передаем ему ключ для авторизации на серверах Telegram
    mybot = Updater(settings.API_KEY, use_context = True)
    # Объявляем диспетчера и добавляем обработчик для команды /start
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler("planet", find_constellation))
    dp.add_handler(CommandHandler('wordcount', count_words))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(CommandHandler('guess', guess_number))
    dp.add_handler(CommandHandler('toad', send_toad_picture))
    dp.add_handler(CommandHandler('cities', play_cities))
    dp.add_handler(CommandHandler('calc', talk_to_calculate))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has been lauched')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()

# Вызываем бота
if __name__ == '__main__':
    main()