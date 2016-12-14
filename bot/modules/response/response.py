from .message import prepare_message, Message
from .markup import prepare_markup


class Response:

    def __init__(self, message, markup=None, **options):
        assert isinstance(message, Message)

        self.message = message
        self.markup = markup
        self.options = options


_transform = dict(
    message=prepare_message,
    markup=prepare_markup
)


def prepare_response(response):
    if isinstance(response, Response):
        return response

    if isinstance(response, str):
        return Response(message=prepare_message(response))

    if isinstance(response, tuple):
        return Response(**dict(map(
            lambda _type, data: (_type, _transform[_type](data)),
            ('message', 'markup'),
            response
        )))
