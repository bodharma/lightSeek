from lightSeeker import LOE
import json
import os

from telegram.ext import Dispatcher, MessageHandler, Filters
from telegram import Update, Bot


bot = Bot(token=os.environ['TELEGRAM_TOKEN'])
dispatcher = Dispatcher(bot=bot, update_queue=None, use_context=True)


def echo(update, context):
    loe = LOE()
    light_status = loe.pretty_message()

    chat_id = update.message.chat_id
    chat_user = update.message.from_user
    chat_text = update.message.text

    context.bot.send_message(chat_id=chat_id, text=light_status)


def lambda_handler(event, context):
    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    try:
        dispatcher.process_update(
            Update.de_json(json.loads(event["body"]), bot)
        )

    except Exception as e:
        print(e)
        return {"statusCode": 500, 'error': f'{e}'}

    return {"statusCode": 200}