import logging

from telebot import TeleBot
from telebot.types import *
from telebot.apihelper import ApiException
from .response import Response


class DelegatorBot:
    def __init__(self, api_token: str, delegate=None):
        self.delegate = delegate
        self.webhook_url = ''
        self.telebot = TeleBot(api_token)

    def init_hook(self, webhook_url: str):
        try:
            self.webhook_url = webhook_url
            return self.telebot.set_webhook(webhook_url)
        except ApiException:
            logging.exception('Cannot initialize web hook')

    def process_update(self, user, update):
        assert isinstance(user, User)
        assert isinstance(update, Update)
        message = update.message

        # Command
        if message is not None and message.text.lstrip().startswith('/'):
            return self.delegate.handle_command(user, update)

        # Simple message
        if message is not None:
            return self.delegate.handle_update(user, update)

    def send_response(self, chat_id, response):
        assert isinstance(response, Response)
        self.telebot.send_message(
            chat_id,
            str.strip(response.message.text),
            parse_mode=response.message.parse_mode,
            reply_markup=response.markup,
            **response.options
        )

    def update_message(self, message_id, chat_id, response):
        assert isinstance(response.markup, InlineKeyboardMarkup)
        self.telebot.edit_message_text(
            str.strip(response.message.text),
            chat_id,
            message_id,
            parse_mode=response.message.parse_mode,
            reply_markup=response.markup,
            **response.options
        )

    def update_message_markup(self, message_id, chat_id, markup):
        assert isinstance(markup, InlineKeyboardMarkup)
        self.telebot.edit_message_reply_markup(
            chat_id,
            message_id,
            reply_markup=markup
        )
