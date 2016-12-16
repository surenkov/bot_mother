import io
from abc import ABCMeta, abstractmethod

from .message import prepare_message, Message
from .markup import prepare_markup
from ..bot import DelegatorBot


class ResponseBase(metaclass=ABCMeta):

    def __init__(self, markup=None, **options):
        self.markup = markup
        self.options = options

    @abstractmethod
    def send_to(self, bot, chat_id):
        pass


class FileResponseBase(ResponseBase, metaclass=ABCMeta):

    def __init__(self, data, caption=None, **options):
        assert isinstance(data, (str, io.IOBase))
        super(FileResponseBase, self).__init__(**options)
        self.data = data
        self.caption = caption


class TextResponse(ResponseBase):

    def __init__(self, message, **options):
        assert isinstance(message, Message)
        super(TextResponse, self).__init__(**options)
        self.message = message

    def send_to(self, bot, chat_id):
        assert isinstance(bot, DelegatorBot)
        return bot.telebot.send_message(
            chat_id,
            self.message.text,
            parse_mode=self.message.parse_mode,
            reply_markup=self.markup,
            **self.options
        )


class PhotoResponse(FileResponseBase):

    def send_to(self, bot, chat_id):
        assert isinstance(bot, DelegatorBot)
        return bot.telebot.send_photo(
            chat_id,
            self.data,
            caption=self.caption,
            reply_markup=self.markup,
            **self.options
        )


class AudioResponse(FileResponseBase):

    def send_to(self, bot, chat_id):
        assert isinstance(bot, DelegatorBot)
        return bot.telebot.send_audio(
            chat_id,
            self.data,
            caption=self.caption,
            reply_markup=self.markup,
            **self.options
        )


class VideoResponse(FileResponseBase):

    def __init__(self, video, **options):
        assert isinstance(video, (str, io.IOBase))
        super(VideoResponse, self).__init__(**options)
        self.video = video

    def send_to(self, bot, chat_id):
        assert isinstance(bot, DelegatorBot)
        return bot.telebot.send_video(
            chat_id,
            self.video,
            caption=self.caption,
            reply_markup=self.markup,
            **self.options
        )


class DocumentResponse(FileResponseBase):

    def send_to(self, bot: DelegatorBot, chat_id):
        return bot.telebot.send_document(
            chat_id,
            self.data,
            caption=self.caption,
            reply_markup=self.markup,
            **self.options
        )


class TextUpdate(TextResponse):
    def __init__(self, message, message_id, **options):
        assert message_id is not None
        super(TextUpdate, self).__init__(message, **options)
        self.message_id = message_id

    def send_to(self, bot, chat_id):
        assert isinstance(bot, DelegatorBot)
        return bot.telebot.edit_message_text(
            self.message.text,
            chat_id,
            self.message_id,
            parse_mode=self.message.parse_mode,
            reply_markup=self.markup,
            **self.options
        )


class MarkupUpdate(ResponseBase):

    def __init__(self, message_id, **options):
        assert message_id is not None
        super(MarkupUpdate, self).__init__(**options)
        self.message_id = message_id

    def send_to(self, bot, chat_id):
        assert isinstance(bot, DelegatorBot)
        return bot.telebot.edit_message_reply_markup(
            chat_id,
            self.message_id,
            reply_markup=self.markup,
            **self.options
        )


def prepare_response(response):
    if isinstance(response, ResponseBase):
        return response

    if isinstance(response, str):
        return TextResponse(
            message=prepare_message(response),
            markup=prepare_markup(None)
        )

    if isinstance(response, tuple):
        res_len = len(response)
        assert res_len > 0

        props = dict()
        if isinstance(response[0], str):
            props['message'] = prepare_message(response[0])
            if res_len > 1 and isinstance(response[1], (list, tuple)):
                props['markup'] = prepare_markup(response[1])
            return TextResponse(**props)

        if isinstance(response[0], io.IOBase):
            props['data'] = response[0]
            if res_len > 1:
                if isinstance(response[1], (list, tuple)):
                    props['markup'] = prepare_markup(response[1])

                if isinstance(response[1], str):
                    props['caption'] = response[1]
                    if res_len > 2 and isinstance(response[2], (list, tuple)):
                        props['markup'] = prepare_markup(response[2])

            return PhotoResponse(**props)
