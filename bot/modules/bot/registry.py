
class BotRegistry:

    def __init__(self):
        self._registry = dict()

    def register(self, bot):
        self._registry[bot.api_token] = bot

    def get(self, api_token: str):
        assert isinstance(api_token, str)
        return self._registry.get(api_token)
