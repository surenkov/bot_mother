import logging
from telebot import TeleBot
from telebot.types import *
from telebot.apihelper import ApiException

from django.conf import settings

from bot.models import TelegramUser
from bot.modules.modules import ModuleRouter
from bot.modules.dispatchers import ResponseDispatcher


class TelegramBot:

    def __init__(self, api_token: str, router: ModuleRouter):
        assert isinstance(api_token, str)
        assert isinstance(router, ModuleRouter)

        self.api_token = api_token
        self.router = router
        self.tele_bot = TeleBot(api_token)
        self.response_dispatcher = ResponseDispatcher(api_token)

    def init_hook(self, webhook_url: str):
        try:
            options = {}
            if hasattr(settings, 'BOT_CERTIFICATE'):
                options['certificate'] = open(settings.BOT_CERTIFICATE)
            return self.tele_bot.set_webhook(webhook_url, **options)
        except ApiException:
            logging.exception('Cannot initialize web hook')

    def process_update(self, update: Update):
        assert isinstance(update, Update)

        user = TelegramUser.from_update(update)
        module = self.router.get(user.get_context('module'))
        if module is None:
            raise Exception(
                'Cannot find appropriate module for {}'.format(user))

        module.handle_update(self.response_dispatcher, user, update)
        user.save()


class BotRegistry:

    def __init__(self):
        self._registry = dict()

    def register(self, bot: TelegramBot):
        assert isinstance(bot, TelegramBot)
        self._registry[bot.api_token] = bot

    def get(self, api_token: str):
        assert isinstance(api_token, str)
        return self._registry.get(api_token)
