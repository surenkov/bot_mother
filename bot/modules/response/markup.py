from telebot.types import *


def prepare_markup(markup):
    if isinstance(markup, (
        ReplyKeyboardMarkup,
        ReplyKeyboardRemove,
        InlineKeyboardMarkup
    )):
        return markup

    if isinstance(markup, (list, tuple)):
        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True
        )
        for row in markup:
            if isinstance(row, str):
                keyboard.add(KeyboardButton(row))
            else:
                keyboard.add(*map(KeyboardButton, row))
        return keyboard

    return ReplyKeyboardRemove()
