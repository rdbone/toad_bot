import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# импортируем файл с конфигами
import settings

logging.basicConfig(filename='bot.log', level=logging.INFO)

# Создаем функцию для приветствия пользователя
def greet_user(update, context):
    # пишем в консоль
    print('Вызван /start')
    print(update)
    # приветствуем пользователя
    update.message.reply_text(settings.GREETING_MESSAGE)

# Создаем функцию для ответа пользователю его же сообщением
def talk_to_me(update, context):
    text = update.message.text
    # пишем в консоль
    print(text)
    # ответим пользователю его же сообщением
    update.message.reply_text(text)

# Тело бота
def main():
    # Создаем бота и передаем ему ключ для авторизации на серверах Telegram
    mybot = Updater(settings.API_KEY, use_context = True)
    # Объявляем диспетчера и добавляем обработчик для команды /start
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))

    logging.info('Bot has been lauched')
    # Командуем боту начать ходить в Telegram за сообщениями
    mybot.start_polling()
    # Запускаем бота, он будет работать, пока мы его не остановим принудительно
    mybot.idle()

# Вызываем бота
if __name__ == '__main__':
    main()