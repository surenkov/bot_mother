
class Message:

    def __init__(self, text, parse_mode=None):
        self.text = text,
        self.parse_mode = parse_mode


class HTML(Message):

    def __init__(self, text):
        super().__init__(text, parse_mode='HTML')


class Markdown(Message):

    def __init__(self, text):
        super().__init__(text, parse_mode='Markdown')


def prepare_message(message):
    if isinstance(message, Message):
        return message

    if isinstance(message, str):
        return Message(message)
