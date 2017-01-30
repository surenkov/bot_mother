import logging
from abc import ABCMeta, abstractmethod
from itertools import repeat, chain, starmap

from telebot.types import Update


class UpdateScenarioBase(metaclass=ABCMeta):
    @abstractmethod
    def can_handle(self, user, update):
        pass

    @abstractmethod
    def handle_update(self, bot, user, update):
        pass


class CallbackQueryScenario(UpdateScenarioBase):
    def __init__(self):
        self.handlers = list()

    def can_handle(self, user, update):
        return update.callback_query is not None

    def handler(self, predicate):
        """
        Decorator, which registers function and predicate as callback query
        handler
        :param predicate: query acceptance predicate
        :return: decorator
        """
        assert callable(predicate)

        def decorator(handler):
            assert callable(handler)
            self.handlers.append((predicate, handler))
            return handler

        return decorator

    def handle_update(self, bot, user, update):
        from bot.models import TelegramUser
        assert isinstance(update, Update)
        assert isinstance(user, TelegramUser)

        accepted_predicates = filter(
            lambda cq: cq[0](user, update.callback_query),
            self.handlers
        )
        try:
            _, handler = next(accepted_predicates)
            handler(bot, user, update.callback_query)
        except StopIteration:
            logging.warning('There is no handler for received callback query')


class MessageScenario(UpdateScenarioBase):
    def __init__(self):
        self.transitions = dict()
        self.commands = dict()
        self.command_aliases = dict()

    def can_handle(self, user, update):
        return update.message is not None

    def message_handler(self, *states):
        """
        Decorator, which sets decorated function as message handler
        for specific states
        :param states: expected states for decorated handler
        :return: decorator
        """
        assert len(states) > 0

        def handler_setter(handler):
            assert callable(handler)
            self.transitions.update(dict(zip(states, repeat(handler))))
            return handler

        return handler_setter

    def command_handler(self, *commands, **aliases):
        """
        Decorator, which sets decorated function as command handler
        for each command in commands
        :param commands: command names
        :return: decorator
        """
        assert len(commands) > 0

        def handler_setter(handler):
            assert callable(handler)
            self.commands.update(zip(
                chain(commands, aliases.keys()), repeat(handler)
            ))
            self.command_aliases.update(starmap(
                lambda command, alias: (alias.lower(), command),
                aliases.items()
            ))
            return handler

        return handler_setter

    def handle_update(self, bot, user, update):
        from bot.models import TelegramUser
        assert isinstance(user, TelegramUser)
        assert isinstance(update, Update)

        handler = None
        message_text = update.message.text.strip().lower()

        if message_text.startswith('/'):
            handler = self.commands.get(message_text.split(maxsplit=1)[0][1:])

        elif message_text in self.command_aliases:
            handler = self.commands.get(self.command_aliases.get(message_text))

        if handler is None:
            state = user.get_context('state')
            handler = self.transitions.get(state)

        if handler is not None:
            handler(bot, user, update.message)
        else:
            logging.warning('No handler found for {} with message "{}"'
                            .format(user, update.message.text))
