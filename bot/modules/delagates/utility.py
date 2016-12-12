from functools import reduce, partial
from bot.models.user import User


def apply_middleware(user, data, handlers):
    assert isinstance(handlers, list)
    assert isinstance(user, User)

    reduced_data = reduce(partial(middleware_reducer, user), handlers, data)
    assert type(reduced_data) is type(data)
    return reduced_data


def middleware_reducer(user, data, func):
    new_data = func(user, data)
    assert new_data is not None
    return new_data
