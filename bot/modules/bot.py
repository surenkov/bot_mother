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
            self.webhook_url = webhook_url
            return self.telebot.set_webhook(webhook_url)
        except ApiException:
            logging.exception('Cannot initialize web hook')

    def process_update(self, user, update):
        assert isinstance(user, User)
        assert isinstance(update, Update)

        message = update.message
        callback_query = update.callback_query

        # Callback queries
        if callback_query is not None:
            return self.delegate.handle_callback_query(user, update)

        # Command
        if message is not None and message.text.lstrip().startswith('/'):
            return self.delegate.handle_command(user, update)

        # Simple message
        if message is not None:
            return self.delegate.handle_update(user, update)
