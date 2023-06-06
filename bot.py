import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from handlers import (count_words, find_constellation, greet_user, guess_number, next_full_moon, 
                      play_cities, send_toad_picture, talk_to_calculate, talk_to_me, user_coordinates)
import settings

logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

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
    dp.add_handler(MessageHandler(Filters.regex('^Рандомный жабокрад$'), send_toad_picture))
    dp.add_handler(MessageHandler(Filters.location, user_coordinates))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has been lauched')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()

# Вызываем бота
if __name__ == '__main__':
    main()