
class BaseModule:

    def __init__(self, context, user):
        self.context = context
        self.user = user

    def dispatch(self, update):
        pass
