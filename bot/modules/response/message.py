
class Message:

    def __init__(self, text, **options):
        self.text = text,
        self.options = options


class HTML(Message):

    def __init__(self, text, **options):
        super(HTML, self).__init__(text, parse_mode='HTML', **options)


class Markdown(Message):

    def __init__(self, text, **options):
        super(Markdown, self).__init__(text, parse_mode='Markdown', **options)


def prepare_message(message):
    if isinstance(message, Message):
        return message

    if isinstance(message, str):
        return Message(message)
