from telebot import TeleBot

from . import app
from ..responses import ResponseBase


@app.task(name='bot.telegram.send_message', rate_limit='30/s', queue='default')
def send_telegram_message(token, chat_id, response):
    """
    Sends message to specific chat
    :param token: bot's token
    :param chat_id: chat id
    :param response: Response object
    :return: result of message sending
    """
    assert isinstance(token, str)
    assert isinstance(response, ResponseBase)
    return response.send_to(TeleBot(token), chat_id)
