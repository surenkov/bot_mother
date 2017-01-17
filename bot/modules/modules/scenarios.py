import logging
from abc import ABCMeta, abstractmethod
from itertools import repeat

from telebot.types import Update


class UpdateScenarioBase(metaclass=ABCMeta):
    @abstractmethod
    def can_handle(self, user, update, handled):
        pass

    @abstractmethod
    def handler(self, *args, **kwargs):
        pass

    @abstractmethod
    def handle_update(self, bot, user, update):
        pass


class CallbackQueryScenario(UpdateScenarioBase):
    def __init__(self):
        self.handlers = list()

    def can_handle(self, user, update, handled):
        return not handled and update.callback_query is not None

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
            handler(bot, user, update)
        except StopIteration:
            logging.warning('There is no handler for received callback query')


class CommandScenario(UpdateScenarioBase):
    def __init__(self):
        self.handlers = dict()

    def can_handle(self, user, update, handled):
        message = update.message
        return not handled \
            and message is not None \
            and message.text.lstrip().startswith('/')

    def handler(self, *commands):
        """
        Decorator, which sets decorated function as command handler
        for each command in commands
        :param commands: command names
        :return: decorator
        """
        assert len(commands) > 0

        def handler_setter(handler):
            assert callable(handler)
            self.handlers.update(dict(zip(commands, repeat(handler))))
            return handler

        return handler_setter

    def handle_update(self, bot, user, update):
        from bot.models import TelegramUser
        assert isinstance(user, TelegramUser)
        assert isinstance(update, Update)

        command_text = update.message.text.split(maxsplit=1)[0][1:]
        handler = self.handlers.get(command_text)

        if handler is not None:
            handler(bot, user, update)
        else:
            logging.info('No handler for command /%s' % command_text)


class MessageScenario(UpdateScenarioBase):
    def __init__(self):
        self.transitions = dict()

    def can_handle(self, user, update, handled):
        return not handled and update.message is not None

    def handler(self, *states):
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

    def handle_update(self, bot, user, update):
        from bot.models import TelegramUser
        assert isinstance(user, TelegramUser)
        assert isinstance(update, Update)

        state = user.get_context('state')
        handler = self.transitions.get(state)
        if handler is not None:
            handler(bot, user, update)
        else:
            logging.warning(
                'No transition form state {} for user {}'.format(state, user))
