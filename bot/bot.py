import logging
from telebot import TeleBot
from telebot.types import *
from telebot.apihelper import ApiException


class DelegatorBot:
    def __init__(self, api_token: str, delegate=None):
        self.delegate = delegate
        self.webhook_url = ''
        self.telebot = TeleBot(api_token)

    def init_hook(self, webhook_url: str):
        try:
            self._init_handlers()
            self.webhook_url = webhook_url
            return self.telebot.set_webhook(webhook_url)
        except ApiException:
            logging.exception('Cannot initialize webhook')

    def handle_update(self, update: Update):
        self.telebot.process_new_updates([update])

    def _init_handlers(self):
        bot = self.telebot
        bot.add_message_handler({
            'function': self.process_command,
            'filters': {'func': lambda m: m.text.lstrip().startswith('/')}
        })
        bot.add_message_handler({
            'function': self.process_update,
            'filters': {'func': lambda _: True}
        })

    def send_response(self, chat_id, response, inline_buttons=None):  # TODO: add inline in response
        if response.keyboard is not None:
            markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            for row in response.keyboard:
                markup.add(*map(KeyboardButton, row))
        else:
            markup = ReplyKeyboardRemove()

        if inline_buttons is not None:
            markup = []
            for row in inline_buttons:
                inline_markup_row = []
                for button in row:
                    inline_markup_row.append(InlineKeyboardButton(text=button))
                markup.append(inline_markup_row)

        self.telebot.send_message(
            chat_id,
            str.strip(response.message.text),
            reply_markup=markup,
            disable_web_page_preview=False,
        )

    def update_message(self, text, buttons, message_id):
        pass
