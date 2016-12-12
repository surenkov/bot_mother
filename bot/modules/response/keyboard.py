

class ReplyKeyboard:

    def __init__(self, rows=None, **options):
        if rows is None:
            rows = []
        self.rows = rows
        self.options = options

    def add_row(self, *buttons):
        self.rows.append(_prepare_row(buttons))


def _prepare_row(row):
    return list(map(str, row))


def prepare_keyboard(keyboard):
    if isinstance(keyboard, ReplyKeyboard):
        return keyboard

    if isinstance(keyboard, (list, tuple)):
        return ReplyKeyboard(list(map(_prepare_row, keyboard)))
