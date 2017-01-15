from datetime import datetime, timedelta
from django.core.cache import caches

from bot.models import TelegramUser
from bot.queue.tasks import send_message
from bot.modules.responses import ResponseBase


class ResponseDispatcher:

    def __init__(self, api_token: str):
        assert isinstance(api_token, str)
        self.api_token = api_token

    def respond(self, user, response):
        assert isinstance(user, (TelegramUser, int))
        assert isinstance(response, ResponseBase)

        if isinstance(user, TelegramUser):
            user = user.user_id

        # TODO: uncomment 'dat after upgrade to Celery
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
        send_message.delay(self.api_token, user, response)
