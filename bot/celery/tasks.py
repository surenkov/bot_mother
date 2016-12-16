from . import app
from ..modules.bot import DelegatorBot, Response, InlineKeyboardMarkup


@app.task(name='bot.send_message', rate_limit='30/s')
def send_message(token, chat_id, response):
    """
    Sends message to specific chat
    :param token: bot's token
    :param chat_id: chat id
    :param response: Response object
    :return: result of message sending
    """
    assert isinstance(token, str)
    assert isinstance(chat_id, int)

    bot = DelegatorBot(token)
    return bot.send_message(chat_id, response)


@app.task(name='bot.update_message', rate_limit='30/s')
def update_message(token, message_id, chat_id, response):
    """
    Updates existing message or its' markup by message and chat ids
    :param token: bot's token
    :param message_id: message id
    :param chat_id: chat id
    :param response: new Response object or InlineKeyboardMarkup
    :return: result of update
    """
    assert isinstance(token, str)
    assert isinstance(message_id, int)
    assert isinstance(chat_id, int)
    assert isinstance(response, (Response, InlineKeyboardMarkup))

    bot = DelegatorBot(token)
    if isinstance(response, Response):
        return bot.update_message(message_id, chat_id, response)
    if isinstance(response, InlineKeyboardMarkup):
        return bot.update_message_markup(message_id, chat_id, response)
