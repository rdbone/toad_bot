from datetime import date, datetime
from emoji import emojize
import ephem
from glob import glob
import logging
from random import randint, choice
import re
import settings
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

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
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has been lauched')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()

# Вызываем бота
if __name__ == '__main__':
    main()