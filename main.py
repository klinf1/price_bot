import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                          CallbackQueryHandler, MessageHandler, Filters)

import db
import messages


PRICE, SUBSCRIBE, HISTORY, BACK, SEARCH = range(5)

load_dotenv()


def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Price", callback_data=str(PRICE)),
         InlineKeyboardButton("Subscribe", callback_data=str(SUBSCRIBE)),
         InlineKeyboardButton("History", callback_data=str(HISTORY)),
         InlineKeyboardButton('Search for id', callback_data=str(SEARCH))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Please choose one of the following options:",
        reply_markup=reply_markup
    )


def button(update, context):
    query = update.callback_query
    option = int(query.data)

    if option == PRICE:
        context.user_data["state"] = PRICE
        query.edit_message_text(text="Please provide the id parameter:")
    elif option == SUBSCRIBE:
        context.user_data["state"] = SUBSCRIBE
        query.edit_message_text(text="Please provide the id parameter:")
    elif option == HISTORY:
        context.user_data["state"] = HISTORY
        query.edit_message_text(text="Please provide the id parameter:")
    elif option == SEARCH:
        context.user_data['state'] = SEARCH
        query.edit_message_text(messages.SEARCH)
    return option


def get_id(update, context):
    state = context.user_data.get("state", None)
    if state == PRICE:
        price_function(update, context)
    elif state == SUBSCRIBE:
        sub_function(update, context)
    elif state == HISTORY:
        history_function(update, context)
    elif state == SEARCH:
        search_function(update, context)
    context.user_data.pop("state", None)


def price_function(update, context):
    id = update.message.text
    data, name = db.get_current_data(id)
    if data:
        message = (f'Data for {name[0]} at {data[4]} server time.\n'
                   f'Price: {data[1]/10000} gold\n'
                   f'Amount: {data[2]}\n'
                   f'Sellers: {data[3]}')
    else:
        message = 'The item with the id you provided is not a commodity!'
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.user_data["state"] = BACK
    back_function(update, context)


def sub_function(update, context):
    update.message.reply_text('This function is currently in development!')
    context.user_data["state"] = BACK
    back_function(update, context)


def history_function(update, context):
    update.message.reply_text('This function is currently in development!')
    context.user_data["state"] = BACK
    back_function(update, context)


def search_function(update, context):
    name = update.message.text
    data = db.get_id_by_name(name)
    if data:
        update.message.reply_text(
            'You were probably looking for one of these:'
        )
        for item in data:
            message = (f'Id: {item[0]}\n'
                       f'name: {item[1]}\n'
                       f'Class: {item[2]}, {item[3]}\n'
                       f'Description: {item[4]}')
            update.message.reply_text(message)
    else:
        update.message.reply_text(
            'Sorry, I could not find an item with the name like this'
        )
    context.user_data["state"] = BACK
    back_function(update, context)


def back_function(update, context):
    state = context.user_data.get("state", None)
    if state == BACK:
        start(update, context)


def main():
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, get_id
    ))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
