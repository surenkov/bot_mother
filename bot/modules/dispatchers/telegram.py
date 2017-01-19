import redis

from datetime import datetime, timedelta
from django.conf import settings

from ..responses import ResponseBase
from ..celery.tasks import send_telegram_message


class CeleryDispatcher:
    _redis_conn = redis.from_url(settings.RESPONSE_TIMESTAMP_REDIS_CONN)

    def __init__(self, api_token: str):
        assert isinstance(api_token, str)
        self.api_token = api_token

    def respond(self, user, response):
        from bot.models import TelegramUser
        assert isinstance(user, (TelegramUser, int))
        assert isinstance(response, ResponseBase)

        if isinstance(user, TelegramUser):
            user = user.user_id

        current_ts = (datetime.utcnow() - timedelta(seconds=1)).timestamp()
        new_ts = max(
            float(self._redis_conn.get(user) or current_ts) + 1,
            current_ts + response.delay + 1
        )
        self._redis_conn.setex(user, new_ts, 1)
        return send_telegram_message.apply_async(
            (self.api_token, user, response),
            eta=datetime.utcfromtimestamp(current_ts)
        )
