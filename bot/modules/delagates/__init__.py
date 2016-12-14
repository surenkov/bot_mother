import types
from itertools import repeat
from telebot.types import Update

from bot.models import User
from ..response import prepare_response
from .utility import apply_middleware


class ModuleDelegate:

    def __init__(self):
        self.entry_point_handler = None
        self.update_handlers = list()
        self.response_handlers = list()
        self.command_handlers = dict()

    def entry_point(self, func):
        """
        Decorator, which sets generator factory func as module entry point
        :param func: generator factory
        :return: func
        """
        self.entry_point_handler = func
        return func

    def update_middleware(self, func):
        """
        Decorator, which registers func as update middleware
        :param func: update middleware function, must accept user and update
            models and return update instance
        :return: func
        """
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
            self.register_command(commands, func)
            return func
        return handler_setter

    def register_command(self, command_or_list, func):
        """
        Register func as handler for commands
        :param command_or_list: command string or list of command strings
        :param func: commands' handler
        """
        if isinstance(command_or_list, str):
            self.command_handlers[command_or_list] = func
        else:
            assert len(command_or_list) > 0
            self.command_handlers.update(
                dict(zip(command_or_list, repeat(func)))
            )

    def handle_update(self, user, update):
        assert callable(self.entry_point_handler)
        assert isinstance(update, Update)
        assert isinstance(user, User)

        gen = user.state
        if gen is None:
            gen = self.entry_point_handler(user)
        assert isinstance(gen, types.GeneratorType)

        try:
            response = apply_middleware(
                user,
                gen.send(apply_middleware(user, update, self.update_handlers)),
                self.response_handlers,
            )
        except StopIteration:
            user.state = None
            response = self.handle_update(user, update)
        else:
            user.state = gen
        return prepare_response(response)

    def handle_command(self, user, update):
        assert isinstance(update, Update)
        assert isinstance(user, User)

        handler = self.command_handlers.get(update.message.text.strip()[1:])
        if handler is None:
            return self.handle_update(user, update)

        response = apply_middleware(
            user,
            handler(user, apply_middleware(user, update, self.update_handlers)),
            self.response_handlers
        )
        return prepare_response(response)
