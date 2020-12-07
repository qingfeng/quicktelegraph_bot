#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
import logging
import urllib.parse
import json
import requests

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = 'YOUR_TOKEN'
REQUEST_KWARGS = {
    'proxy_url': 'http://127.0.0.1:1087/',
}

API_URL = "https://api.telegra.ph"
# IDEA add photo type
TITLE, CONTENT, PHOTO = range(3)


def create_telegra_accesstoken():
    params = {
        'short_name': 'Sandbox',
        'author_name': 'Anonymous'
    }

    r = requests.get("%s/createAccount?%s" % (API_URL, urllib.parse.urlencode(params)))
    return r.json()['result']['access_token']


def send_to_telegra(title, content):
    access_token = create_telegra_accesstoken()
    params = {
        'access_token': access_token,
        'author_name': 'Anonymous',
        'title': title,
        'content': '[{"tag":"p","children":[%s]}]' % json.dumps(content, ensure_ascii=False),
        'return_content': 'false'
    }
    r = requests.post('%s/createPage' % API_URL, data=params)
    result = r.json()
    if result['ok']:
        return result['result']['url']


def start(update, context):
    update.message.reply_text("What's the title?")
    return TITLE


def title(update, context):
    title = update.message.text
    context.user_data['title'] = title
    update.message.reply_text("Send the Content.")
    return CONTENT


def content(update, context):
    title = context.user_data['title']
    content = update.message.text
    url = send_to_telegra(title, content)
    update.message.reply_text(url)
    update.message.reply_text('Done, donate to me: https://www.paypal.com/paypalme/asahi001')
    logger.info("Done.")
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text("It all starts /start.")


def cancel(update, context):
    logger.info("canceled the conversation.")
    update.message.reply_text('Bye, canceled the conversation.')

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    logger.info(socket.gethostname())
    if 'qingfengs' in socket.gethostname():
        updater = Updater(TOKEN, use_context=True, request_kwargs=REQUEST_KWARGS)
    else:
        updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            TITLE: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, title)],
            CONTENT: [CommandHandler('cancel', cancel), MessageHandler(Filters.text, content)],

            # PHOTO: [MessageHandler(Filters.photo, photo)),
                    # CommandHandler('skip', skip_photo)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
