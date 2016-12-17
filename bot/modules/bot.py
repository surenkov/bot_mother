import logging
from datetime import datetime, timedelta

from django.core.cache import caches
from telebot import TeleBot
from telebot.types import *
from telebot.apihelper import ApiException

from ..models import User
from ..queue.tasks import send_message


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

    def send_response(self, user, response):
        assert isinstance(user, User)
        if response is not None:
            # TODO: uncomment 'dat after upgrade to PyPy3.5 and Celery
            # cache = caches['user_timestamps']
            # user_cache_key = str(user.user_id)
            #
            # last_response_timestamp = cache.get(user_cache_key)
            # new_timestamp = datetime.now()
            #
            # if last_response_timestamp is not None \
            #         and last_response_timestamp > new_timestamp:
            #     new_timestamp = last_response_timestamp + timedelta(seconds=1)
            #
            # cache.set(user_cache_key, new_timestamp, timeout=1)
            send_message.delay(self.telebot.token, user.user_id, response)
        else:
            logging.info('No response was given')
