import types
from functools import reduce

from ..response import prepare_response
from bot.models.user import User
from telebot.types import Update


class DelegateBot:

    def __init__(self, token=None):
        self.entry_point_handler = None
        self.update_handlers = []
        self.response_handlers = []

    def entry_point(self, func=None):
        self.entry_point_handler = func
        return func

    def update_middleware(self, func):
        self.update_handlers.append(func)
        return func

    def response_middleware(self, func):
        self.response_handlers.append(func)
        return func

    def handle_update(self, user, update):
        assert callable(self.entry_point_handler)
        assert isinstance(user, User)
        assert isinstance(update, Update)

        gen = user.state
        if gen is None or update.message.text == '/start':
            gen = self.entry_point_handler(user)
        assert isinstance(gen, types.GeneratorType)

        processed_update = reduce(reducer, self.update_handlers, update)
        assert isinstance(processed_update, Update)

        try:
            response = reduce(
                reducer,
                self.response_handlers,
                gen.send(processed_update)
            )
        except StopIteration:
            user.state = None
            response = self.handle_update(user, update)
        else:
            user.state = gen
        return prepare_response(response)


def reducer(value, handler):
    return handler(value)


