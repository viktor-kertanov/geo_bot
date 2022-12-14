from config import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import API_TOKEN


def greet_user(update, context):
    print('Вызван /start, vk')
    update.message.reply_text(f"Привет! {update}")

def talk_to_me(update, context):
    text_to_repeat = update.message.text
    update.message.reply_text(text_to_repeat)

    internal_msg = f'We have just echoed: "{text_to_repeat}"'
    logging.info(internal_msg)
    print(internal_msg)
    return

def main():
    echo_bot = Updater(API_TOKEN, use_context=True)
    
    #dispatcher & registering handlers
    dp = echo_bot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me))
    logging.info('Бот стартовал')
    
    echo_bot.start_polling()
    echo_bot.idle()


if __name__ == '__main__':
    main()
