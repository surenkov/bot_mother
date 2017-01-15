from bot.modules.responses import prepare_response


class MiddlewareBotProxy:

    def __init__(self, bot, middleware):
        self.bot = bot
        self.middleware = middleware

    def respond(self, user, response):
        return self.bot.respond(
            user,
            self.middleware.apply_response(user, prepare_response(response))
        )


class StopUpdateProcessing(Exception):
    pass
