import logging
from telebot.types import Update

from .scenarios import UpdateScenarioBase
from .utility import StopUpdateProcessing
from .middleware import Middleware


class Module:

    def __init__(self, name, initial_state, scenarios=None, middleware=None):
        self.name = name
        self.initial_state = initial_state
        self.scenarios = scenarios or list()
        self.middleware = middleware or Middleware()

    def handle_update(self, bot, user, update):
        from bot.models import TelegramUser
        from .utility import MiddlewareBotProxy

        assert isinstance(user, TelegramUser)
        assert isinstance(update, Update)

        state = user.get_context('state')
        user.set_context(state=state or self.initial_state)

        try:
            update = self.middleware.apply_update(user, update)
            bot_proxy = MiddlewareBotProxy(bot, self.middleware)
            handled = False

            for update_handler in self.scenarios:
                can_handle = update_handler.can_handle(user, update, handled)
                if can_handle:
                    update_handler.handle_update(bot_proxy, user, update)
                handled |= can_handle

            if not handled:
                logging.warning('{}\'s response was not handled'.format(user))
        except StopUpdateProcessing:
            pass

    def add_scenario(self, scenario: UpdateScenarioBase):
        assert isinstance(scenarios, UpdateScenarioBase)
        self.scenarios.append(scenario)


class ModuleRouter:

    def __init__(self, initial=None):
        assert isinstance(initial, (Module, str))

        self.initial = initial
        self._registry = dict()

        if isinstance(initial, Module):
            self.register(initial)
            self.initial = initial.name

    def register(self, module):
        assert isinstance(module, Module)
        self._registry[module.name] = module

    def get(self, name=None):
        if name is None:
            name = self.initial
        return self._registry.get(name)
