import logging
import types
from itertools import repeat
from functools import partial
from telebot.types import Update

from bot.models import User
from ..response import prepare_response
from .utility import apply_middleware, process_generator


class ModuleDelegate:
    def __init__(self):
        self.entry_point_handler = None
        self.update_handlers = list()
        self.response_handlers = list()
        self.command_handlers = dict()
        self.callback_query_handlers = list()

    def entry_point(self, func):
        """
        Decorator, which sets generator factory func as module entry point
        :param func: generator factory
        :return: func
        """
        assert callable(func)
        self.entry_point_handler = func
        return func

    def update_middleware(self, func):
        """
        Decorator, which registers func as update middleware
        :param func: update middleware function, must accept user and update
            models and return update instance
        :return: func
        """
        assert callable(func)
        self.update_handlers.append(func)
        return func

    def response_middleware(self, func):
        """
        Decorator, which registers func as response middleware
        :param func: response middleware function, must accept
            user and response models and return response instance
        :return: func
        """
        self.response_handlers.append(func)
        return func

    def command(self, *commands):
        """
        Decorator, which sets decorated function as command handler
        for each command in commands
        :param commands: command names
        :return: decorator
        """
        assert len(commands) > 0

        def handler_setter(func):
            assert callable(func)
            self.register_command(commands, func)
            return func

        return handler_setter

    def register_command(self, command_or_list, func):
        """
        Register func as handler for commands
        :param command_or_list: command string or list of command strings
        :param func: commands' handler
        """
        assert callable(func)
        if isinstance(command_or_list, str):
            self.command_handlers[command_or_list] = func
        else:
            assert len(command_or_list) > 0
            self.command_handlers.update(
                dict(zip(command_or_list, repeat(func)))
            )

    def callback_query(self, predicate):
        """
        Decorator, which registers function and predicate as callback query
        handler
        :param predicate: query acceptance predicate
        :return: decorator
        """

        def decorator(func):
            self.register_callback_query(predicate, func)
            return func

        return decorator

    def register_callback_query(self, predicate, handler):
        assert callable(predicate)
        assert callable(handler)
        self.callback_query_handlers.append((predicate, handler))

    def handle_update(self, user, update):
        assert callable(self.entry_point_handler)
        assert isinstance(update, Update)
        assert isinstance(user, User)

        gen = user.state
        initial = gen is None

        if initial:
            gen = self.entry_point_handler(user)

        assert isinstance(gen, types.GeneratorType)

        try:
            response = self._generate_response(
                partial(process_generator, gen, initial=initial),
                user, update)
        except StopIteration:
            user.state = None
            response = self.handle_update(user, update)
        else:
            user.state = gen
        return prepare_response(response)

    def handle_command(self, user, update):
        assert isinstance(update, Update)
        assert isinstance(user, User)

        prep_command = update.message.text.split(maxsplit=1)[0][1:]
        handler = self.command_handlers.get(prep_command)
        if handler is None:
            return self.handle_update(user, update)

        response = self._generate_response(
            partial(handler, user), user, update)
        return prepare_response(response)

    def handle_callback_query(self, user, update):
        assert isinstance(user, User)
        assert isinstance(update, Update)

        accepted_predicates = filter(
            lambda cq: cq[0](user, update.callback_query),
            self.callback_query_handlers
        )
        try:
            _, handler = next(accepted_predicates)
            response = self._generate_response(
                partial(handler, user), user, update)
            return prepare_response(response)
        except StopIteration:
            logging.info('There is no handler for received callback query')

    def _generate_response(self, callback, user, update):
        return apply_middleware(
            user,
            callback(apply_middleware(user, update, self.update_handlers)),
            self.response_handlers
        )
