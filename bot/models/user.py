import json
import redis

from django.db import models
from django.conf import settings

from telebot.types import Update


class TelegramUser(models.Model):
    _redis_conn = redis.from_url(settings.USER_CONTEXT_REDIS_CONN)

    user_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)

    def __str__(self):
        full_name = self.first_name
        if self.last_name is not None:
            full_name += ' ' + self.last_name
        if self.username is not None:
            full_name += ' (@' + self.username + ')'
        return full_name

    def get_context(self, field=None):
        context = _decode_context(self._redis_conn.lindex(self.user_id, 0))
        if field is not None:
            return context.get(field)
        return context

    def set_context(self, inherit=True, **context):
        conn = self._redis_conn
        new_context = dict()
        stack_head = conn.lpop(self.user_id)

        if inherit:
            new_context.update(_decode_context(stack_head))

        new_context.update(context)
        return conn.lpush(self.user_id, _encode_context(new_context))

    def setdefault_context(self, **context):
        conn = self._redis_conn
        context.update(_decode_context(conn.lpop(self.user_id)))
        return conn.lpush(self.user_id, _encode_context(context))

    def push_context(self, inherit=True, **context):
        conn = self._redis_conn
        new_context = dict()

        if inherit:
            new_context.update(_decode_context(conn.lindex(self.user_id, 0)))

        new_context.update(context)
        return conn.lpush(self.user_id, _encode_context(new_context))

    def pop_context(self, empty=False):
        conn = self._redis_conn
        if empty:
            conn.delete(self.user_id)
        return _decode_context(conn.lpop(self.user_id))

    @staticmethod
    def from_update(update: Update):
        assert isinstance(update, Update)
        telegram_user = None

        message = update.message
        edited_message = update.edited_message
        callback_query = update.callback_query

        if message is not None:
            telegram_user = message.from_user
        elif edited_message is not None:
            telegram_user = edited_message.from_user
        elif callback_query is not None:
            telegram_user = callback_query.from_user

        assert telegram_user is not None
        user, _ = TelegramUser.objects.get_or_create(
            user_id=telegram_user.id,
            defaults=(dict(
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username
            ))
        )
        return user


def _decode_context(data):
    if isinstance(data, (bytes, bytearray)):
        data = data.decode()
    return json.loads(data or '{}')


def _encode_context(data):
    return json.dumps(data or {})
