from .message import prepare_message
from .keyboard import prepare_keyboard


class Response:

    def __init__(self, message=None, keyboard=None, **options):
        self.message = message
        self.keyboard = keyboard
        self.options = options


def prepare_response(response):
    if isinstance(response, Response):
        return response

    if isinstance(response, str):
        return Response(message=prepare_message(response))

    if isinstance(response, tuple):
        msg, kbd = response
        return Response(
            message=prepare_message(msg),
            keyboard=prepare_keyboard(kbd)
        )
