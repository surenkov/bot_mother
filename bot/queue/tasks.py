from telebot import TeleBot
from ..modules.response import ResponseBase


def send_message(token, chat_id, response):
    """
    Sends message to specific chat
    :param token: bot's token
    :param chat_id: chat id
    :param response: Response object
    :return: result of message sending
    """
    assert isinstance(token, str)
    assert isinstance(response, ResponseBase)
    response.send_to(TeleBot(token), chat_id)
