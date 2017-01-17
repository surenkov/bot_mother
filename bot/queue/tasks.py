from telebot import TeleBot
from rq.decorators import job

from . import message_queue
from ..modules.responses import ResponseBase


@job(message_queue, result_ttl=10)
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
    return response.send_to(TeleBot(token), chat_id)
