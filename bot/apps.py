from importlib import import_module
from django.apps import AppConfig
from django.conf import settings


class BotConfig(AppConfig):
    name = 'bot'

    def __init__(self, app_name, app_module):
        super(BotConfig, self).__init__(app_name, app_module)
        self.bot_registry = dict()

    def ready(self):
        from .modules.bot import DelegatorBot

        for token, delegate_path in settings.REGISTERED_BOTS.items():
            module_name, delegate_name = delegate_path.rsplit(':', 1)
            delegate = getattr(import_module(module_name), delegate_name)
            if delegate is None:
                raise ImportError(
                    'Cannot find delegate "%s" in module "%s"' %
                    (delegate_name, module_name)
                )
            self.bot_registry[token] = DelegatorBot(token, delegate)
