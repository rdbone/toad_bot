import logging, settings, ephem
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import date

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

# Создаем функцию для приветствия пользователя
def greet_user(update, context):
    logging.info('Bot has been lauched')
    text = 'Вызван /start'
    print(text)
    update.message.reply_text('Дороу, жабокрад')

# Создаем функцию для ответа пользователю его же сообщением
def talk_to_me(update, context):
    user_text = update.message.text
    logging.info(f'User said {user_text}')
    print(user_text)
    update.message.reply_text(user_text)

# Проверяет, что объект есть в списке объектов пакета ephem
def check_planet(planet):
    for item in ephem._libastro.builtin_planets():
        if planet in str(item):
            return True
    return False    
    

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

# Тело бота
def main():
    # Создаем бота и передаем ему ключ для авторизации на серверах Telegram
    mybot = Updater(settings.API_KEY, use_context = True)
    # Объявляем диспетчера и добавляем обработчик для команды /start
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler("planet", find_constellation))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has been lauched')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()

# Вызываем бота
if __name__ == '__main__':
    main()