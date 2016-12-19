from django.db import models
from telebot.types import Update

from . import fields


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    state = fields.SerializedField(null=True)

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)

    is_authorized = models.BooleanField(default=False)

    def __str__(self):
        full_name = self.first_name
        if self.last_name is not None:
            full_name += ' ' + self.last_name
        if self.username is not None:
            full_name += ' (@' + self.username + ')'
        return full_name


def get_user_from_update(update):
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
    user, _ = User.objects.get_or_create(
        user_id=telegram_user.id,
        defaults=(dict(
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            username=telegram_user.username
        ))
    )
    return user
