import logging
from telebot.types import Update

from bot.models import TelegramUser
from .utility import MiddlewareBotProxy, StopUpdateProcessing
from .middleware import Middleware


class Module:

    def __init__(self, name, initial_state,
                 message_scenario=None, command_scenario=None,
                 query_scenario=None, middleware=None):
        self.name = name
        self.initial_state = initial_state

        self.command_handler = command_scenario
        self.query_handler = query_scenario
        self.message_handler = message_scenario
        self.middleware = middleware or Middleware()

    def handle_update(self, bot, user, update):
        assert isinstance(user, TelegramUser)
        assert isinstance(update, Update)

        state = user.get_context('state')
        user.set_context(state=state or self.initial_state)

        try:
            update = self.middleware.apply_update(user, update)
            bot_proxy = MiddlewareBotProxy(bot, self.middleware)

            message = update.message
            callback_query = update.callback_query

            handled = False
            # Callback queries
            if callback_query is not None:
                handled |= self.query_handler.handle_update(
                    bot_proxy, user, update)

            # Command
            if message is not None and message.text.lstrip().startswith('/'):
                handled |= self.command_handler.handle_update(
                    bot_proxy, user, update)

            # Simple message
            if message is not None and not handled:
                handled |= self.message_handler.handle_update(
                    bot_proxy, user, update)

            if not handled:
                logging.warning('{}\'s response was not handled'.format(user))
        except StopUpdateProcessing:
            pass


class ModuleRouter:

    def __init__(self, initial=None):
        assert isinstance(initial, (Module, str))
        if isinstance(initial, Module):
            self.register(initial)
            initial = initial.name

        self.initial = initial
        self._registry = dict()

    def register(self, module):
        assert isinstance(module, Module)
        self._registry[module.name] = module

    def get(self, name=None):
        if name is None:
            name = self.initial
        return self._registry.get(name)
