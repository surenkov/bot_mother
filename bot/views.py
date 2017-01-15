import logging

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.apps import apps
from telebot.types import Update

from .models.user import get_user_from_update


@csrf_exempt
@require_POST
def bot_endpoint(request, token):
    bot_registry = apps.get_app_config('bot').bot_registry
    bot = bot_registry.get(token)

    if bot is None:
        return HttpResponse(status=404)

    update = Update.de_json(request.body.encode('utf-8'))
    bot.process_update(update)

    return HttpResponse(status=200)
