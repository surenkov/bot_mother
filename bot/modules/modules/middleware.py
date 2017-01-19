from bot.modules.responses import prepare_response


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
        assert callable(func)
        self.response_handlers.append(func)
        return func

    def apply_response(self, user, response):
        for handler in self.response_handlers:
            response = handler(user, response)
        return response

    def apply_update(self, user, update):
        for handler in self.update_handlers:
            update = handler(user, update)
        return update


class MiddlewareProxy:

    def __init__(self, bot, middleware):
        self.bot = bot
        self.middleware = middleware

    def respond(self, user, response):
        return self.bot.respond(
            user,
            self.middleware.apply_response(user, prepare_response(response))
        )
