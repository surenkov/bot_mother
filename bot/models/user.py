from django.db import models
from django.contrib.postgres import fields
from telebot.types import Update


class TelegramUser(models.Model):
    user_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True)
    username = models.CharField(max_length=255, null=True)

    context_stack = fields.JSONField(default=list)

    def __str__(self):
        full_name = self.first_name
        if self.last_name is not None:
            full_name += ' ' + self.last_name
        if self.username is not None:
            full_name += ' (@' + self.username + ')'
        return full_name

    def get_context(self, field=None):
        stack = self.context_stack
        if not stack:
            stack.append({})

        context = stack[-1]
        if field is None:
            return context
        return context.get(field)

    def set_context(self, inherit=True, **context):
        stack = self.context_stack
        if not stack:
            stack.append({})

        new_context = {}
        if inherit:
            new_context.update(stack[-1])

        new_context.update(context)
        stack[-1] = new_context

    def push_context(self, inherit=True, **context):
        stack = self.context_stack

        previous_context = {}
        if stack and inherit:
            previous_context.update(stack[-1])

        previous_context.update(context)
        stack.append(previous_context)

    def pop_context(self):
        stack = self.context_stack
        if stack:
            del stack[-1]

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
