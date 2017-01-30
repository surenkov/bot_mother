from telebot.types import Update

from .scenarios import UpdateScenarioBase
from .middleware import Middleware, MiddlewareProxy


class Module:

    def __init__(self, name, initial_state, scenarios=None, middleware=None):
        """
        :param name: Name, used as module identifier in registry.
        :param initial_state: Initial state for users without state.
        :param scenarios: Scenarios iterable
        :param middleware: Middleware object
        """
        self.name = name
        self.initial_state = initial_state
        self.scenarios = list(scenarios or [])
        self.middleware = middleware or Middleware()

    def handle_update(self, bot, user, update):
        from bot.models import TelegramUser
        assert isinstance(user, TelegramUser)
        assert isinstance(update, Update)

        user.setdefault_context(state=self.initial_state)

        bot_proxy = MiddlewareProxy(bot, self.middleware)
        update = self.middleware.apply_update(user, update)

        for scenario in self.scenarios:
            if scenario.can_handle(user, update):
                scenario.handle_update(bot_proxy, user, update)

    def add_scenario(self, *scenarios):
        self.scenarios.extend(scenarios)

    def set_middleware(self, middleware):
        self.middleware = middleware


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
