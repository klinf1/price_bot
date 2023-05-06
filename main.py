import os

from dotenv import load_dotenv
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InputMediaPhoto, Update)
from telegram.ext import (Updater, CommandHandler,
                          CallbackQueryHandler, MessageHandler,
                          Filters, CallbackContext)

import db
import messages
import utils


PRICE, SUBSCRIBE, HISTORY, BACK, SEARCH, SUB, UNSUB, LIST_SUBS = range(8)
LAST_DAY, LAST_WEEK, LAST_MONTH, EXACT = range(8, 12)

load_dotenv()


def start(update: Update, context: CallbackContext):
    main_menu(update, context)


def main_menu(update: Update, context: CallbackContext):
    context.user_data.pop('State', None)
    keyboard = [
        [InlineKeyboardButton("Price", callback_data=str(PRICE)),
         InlineKeyboardButton("Subscriptions", callback_data=str(SUBSCRIBE)),
         InlineKeyboardButton("History", callback_data=str(HISTORY)),
         InlineKeyboardButton('Search for id', callback_data=str(SEARCH))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages.CHOSE_ONE,
        reply_markup=reply_markup
    )


def subs_menu(update: Update, context: CallbackContext):
    sub_menu_keys = [[InlineKeyboardButton('My subscriptions',
                                           callback_data=str(LIST_SUBS))],
                     [InlineKeyboardButton('Subscribe',
                                           callback_data=str(SUB))],
                     [InlineKeyboardButton('Unsubscribe',
                                           callback_data=str(UNSUB))],
                     [InlineKeyboardButton('Back',
                                           callback_data=str(BACK))]]
    reply_markup = InlineKeyboardMarkup(sub_menu_keys)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages.CHOSE_ONE,
        reply_markup=reply_markup
    )


def history_menu(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton('Last day',
                                      callback_data=str(LAST_DAY))],
                [InlineKeyboardButton('7 days',
                                      callback_data=str(LAST_WEEK))],
                [InlineKeyboardButton('30 days',
                                      callback_data=str(LAST_MONTH))],
                [InlineKeyboardButton('Exact day',
                                      callback_data=str(EXACT))],
                [InlineKeyboardButton('Back',
                                      callback_data=str(BACK))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=messages.CHOSE_ONE,
        reply_markup=reply_markup
    )


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    option = int(query.data)

    if option == PRICE:
        context.user_data["state"] = PRICE
        query.edit_message_text(text=messages.ASK_FOR_ID)
    elif option == SUBSCRIBE:
        context.user_data["state"] = SUBSCRIBE
        query.message.delete()
        subs_menu(update, context)
    elif option == HISTORY:
        context.user_data["state"] = HISTORY
        query.edit_message_text(text=messages.ASK_FOR_ID)
    elif option == SEARCH:
        context.user_data['state'] = SEARCH
        query.edit_message_text(messages.SEARCH)
    elif option == LIST_SUBS:
        query.message.delete()
        data = db.list_subs(update.effective_chat.id)
        context.bot.send_message(
            update.effective_chat.id,
            'Your subscriptions:'
        )
        for item in data:
            if item:
                str_data = (f'Id: {item[0]} \nName: {item[1]}\n',
                            f'Class: {item[2]}\nSubclass: {item[3]}\n')
                context.bot.send_message(
                    update.effective_chat.id,
                    ''.join(str_data)
                )
        return subs_menu(update, context)
    elif option == SUB:
        context.user_data['state'] = SUB
        query.edit_message_text(text=messages.ASK_FOR_ID)
    elif option == UNSUB:
        context.user_data['state'] = UNSUB
        query.edit_message_text(text=messages.ASK_FOR_ID)
    elif option == LAST_DAY:
        context.user_data['state'] = LAST_DAY
        context.user_data['history'] = 'Last day'
        query.message.delete()
        return graph_function(update, context)
    elif option == LAST_WEEK:
        context.user_data['state'] = LAST_WEEK
        context.user_data['history'] = '7 days'
        query.message.delete()
        return graph_function(update, context)
    elif option == LAST_MONTH:
        context.user_data['state'] = LAST_MONTH
        context.user_data['history'] = '30 days'
        query.message.delete()
        return graph_function(update, context)
    elif option == EXACT:
        context.user_data['state'] = EXACT
        query.edit_message_text(
            text='Please, provide the date in YYYY-MM-DD format'
        )
    elif option == BACK:
        query.message.delete()
        return main_menu(update, context)

    return option


def get_id(update: Update, context: CallbackContext):
    state = context.user_data.get("state", None)
    if state == PRICE:
        price_function(update, context)
    elif state == HISTORY:
        context.user_data['requested_id'] = update.message.text
        history_function(update, context)
    elif state == SEARCH:
        search_function(update, context)
    elif state == SUB:
        subscribe(update, context)
    elif state == UNSUB:
        unsubscribe(update, context)
    else:
        update.message.reply_text(
            'Unexpected input! Returning to main menu'
        )
        main_menu(update, context)


def price_function(update: Update, context: CallbackContext):
    id = update.message.text
    data, name = db.get_current_data(id)
    if data:
        message = (f'Data for {name} at {data[4]} server time.\n'
                   f'Price: {data[1]/10000} gold\n'
                   f'Amount: {data[2]}\n'
                   f'Sellers: {data[3]}')
    else:
        message = messages.NOT_A_COMMODITY_ERROR
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    context.user_data.pop('State', None)
    main_menu(update, context)


def subscribe(update: Update, context: CallbackContext):
    if update.message.text in db.get_subs(update.effective_chat.id):
        update.message.reply_text('You are already subscribed!')
    elif utils.check_id_list(update.message.text) is False:
        update.message.reply_text(
            messages.NOT_A_COMMODITY_ERROR
        )
    else:
        db.add_sub(update.effective_chat.id, update.message.text)
        update.message.reply_text(
            f'You are now subscribed to {update.message.text}'
        )
    return subs_menu(update, context)


def unsubscribe(update: Update, context: CallbackContext):
    if utils.check_id_list(update.message.text) is False:
        update.message.reply_text(
            messages.NOT_A_COMMODITY_ERROR
        )
    elif update.message.text not in db.get_subs(update.effective_chat.id):
        update.message.reply_text('You are not subscribed!')
    else:
        db.delete_sub(update.effective_chat.id, update.message.text)
        update.message.reply_text(
            f'You have unsubscribed from {update.message.text}'
        )
    return subs_menu(update, context)


def history_function(update: Update, context: CallbackContext):
    id = context.user_data.get('requested_id')
    if not utils.check_id_list(id):
        context.bot.send_message(
            update.effective_chat.id,
            messages.NOT_A_COMMODITY_ERROR
        )
        return main_menu(update, context)
    history_menu(update, context)


def graph_function(update: Update, context: CallbackContext):
    id = context.user_data.get('requested_id')
    if not utils.check_id_list(id):
        update.message.reply_text(
            messages.NOT_A_COMMODITY_ERROR,
        )
    else:
        period = context.user_data.get('history')
        files = db.get_history_graph(id, period)
        media = [InputMediaPhoto(open(file, 'rb')) for file in files]
        context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=media,
        )
        msg = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Nothing to see here',
        )
        msg.delete()
        if period == '7 days' or period == '30 days':
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=messages.AVG_REMINDER
            )
        for file in files:
            os.remove(file)
    context.user_data.pop("requested_id", None)
    context.user_data.pop('State', None)
    main_menu(update, context)


def exact_graph_function(update: Update, context: CallbackContext):
    date = update.message.text
    id = context.user_data.get('requested_id')
    if not utils.check_date(id, date):
        context.bot.send_message(
            update.effective_chat.id,
            'There is no data availible for that day.'
        )
    else:
        files = db.get_exact_date_graphs(id, date)
        media = [InputMediaPhoto(open(file, 'rb')) for file in files]
        context.bot.send_media_group(
            chat_id=update.effective_chat.id,
            media=media,
        )
        for file in files:
            os.remove(file)
    context.user_data.pop("requested_id", None)
    context.user_data.pop('State', None)
    main_menu(update, context)


def search_function(update: Update, context: CallbackContext):
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
    context.user_data.pop('State', None)
    main_menu(update, context)


def main():
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(MessageHandler(
        Filters.regex(
            '^(19|20)\d\d[- /.](0[1-9]|1[012])[- /.](0[1-9]|[12][0-9]|3[01])$'
        ),
        exact_graph_function
    ))
    dispatcher.add_handler(MessageHandler(
        Filters.regex("^(Last day|7 days|30 days)$"), graph_function
    ))
    dispatcher.add_handler
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command, get_id
    ))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
