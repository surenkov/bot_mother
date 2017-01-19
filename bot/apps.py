from django.apps import AppConfig
from django.conf import settings
from django.shortcuts import reverse


class BotConfig(AppConfig):
    name = 'bot'

    def __init__(self, app_name, app_module):
        from .modules.bot.registry import BotRegistry

        super().__init__(app_name, app_module)
        self.bot_registry = BotRegistry()

    def ready(self):
        # noinspection PyUnresolvedReferences
        import bot.modules.celery
        from bot.modules import TelegramBot, ModuleRouter

        bot = TelegramBot('token', router=ModuleRouter('example_module_name'))
        bot.init_hook('{site}{path}'.format(
            site=settings.BASE_URL,
            path=reverse('bot_endpoint', kwargs={'token': 'token'})
        ))
        self.bot_registry.register(bot)
