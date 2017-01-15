from django.apps import AppConfig
from django.conf import settings
from django.shortcuts import reverse

from bot.modules import TelegramBot, BotRegistry, ModuleRouter


class BotConfig(AppConfig):
    name = 'bot'

    def __init__(self, app_name, app_module):
        super(BotConfig, self).__init__(app_name, app_module)
        self.bot_registry = BotRegistry()

    def ready(self):
        bot = TelegramBot('token', router=ModuleRouter('example_module_name'))
        bot.init_hook('{site}{path}'.format(
            site=settings.BASE_URL,
            path=reverse('bot_endpoint', kwargs={'token': 'token'})
        ))
        self.bot_registry.register(bot)
