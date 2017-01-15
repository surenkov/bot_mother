from functools import reduce, partial


class Middleware:

    def __init__(self):
        self.response_handlers = list()
        self.update_handlers = list()

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

    def apply_response(self, user, response):
        return reduce(
            partial(middleware_reducer, user),
            self.response_handlers,
            response
        )

    def apply_update(self, user, update):
        return reduce(
            partial(middleware_reducer, user),
            self.update_handlers,
            update
        )


def middleware_reducer(user, data, reducer):
    return reducer(user, data)
