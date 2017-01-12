import io
import os
import mimetypes
import magic

from abc import ABCMeta, abstractmethod
from telebot import TeleBot

from .message import prepare_message, Message
from .markup import prepare_markup


class NotAllowedExtensionError(Exception):
    pass


class InvalidTypeError(Exception):
    pass


class ResponseBase(metaclass=ABCMeta):

    def __init__(self, **options):
        self.options = options

    @abstractmethod
    def send_to(self, bot, chat_id):
        pass


class MarkupResponseBase(ResponseBase, metaclass=ABCMeta):

    def __init__(self, markup=None, **options):
        super(MarkupResponseBase, self).__init__(**options)
        self.markup = markup or prepare_markup(None)


class FileResponseBase(MarkupResponseBase, metaclass=ABCMeta):

    def __init__(self, data, caption=None, filename=None, **options):
        assert isinstance(data, (str, bytes, io.BufferedIOBase, io.RawIOBase))
        super(FileResponseBase, self).__init__(**options)

        if isinstance(data, str):
            if os.path.exists(data):
                with open(data, 'rb') as fin:
                    data = fin.readall()

                    if filename is None:
                        filename = fin.name

        elif isinstance(data, (io.BufferedIOBase, io.RawIOBase)):
            data = data.read(-1)

        if filename is None:
            with magic.Magic(mime=True) as m:
                file_type = m.from_buffer(data)

            ext = mimetypes.guess_extension(file_type)
            if ext is None:
                raise InvalidTypeError('Can\'t determine type of data source')

            filename = 'file%s' % ext

        ext = os.path.splitext(filename)[1]
        if not ext \
                or hasattr(self, 'allowed_extensions') \
                and ext[1:] not in getattr(self, 'allowed_extensions'):
            raise NotAllowedExtensionError(
                'File with "%s" extension is not allowed' % ext)

        self.data = data
        self.caption = caption
        self.filename = filename

    def request_buffer(self):
        blob = io.BytesIO(self.data)
        blob.name = self.filename
        return blob


class TextResponse(MarkupResponseBase):

    def __init__(self, message, **options):
        assert isinstance(message, (Message, str))
        super(TextResponse, self).__init__(**options)
        if isinstance(message, str):
            message = Message(message)
        self.message = message

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        return bot.send_message(
            chat_id,
            self.message.text,
            parse_mode=self.message.parse_mode,
            reply_markup=self.markup,
            **self.options
        )


class PhotoResponse(FileResponseBase):

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        with self.request_buffer() as data:
            return bot.send_photo(
                chat_id,
                data,
                caption=self.caption,
                reply_markup=self.markup,
                **self.options
            )


class AudioResponse(FileResponseBase):

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        with self.request_buffer() as data:
            return bot.send_audio(
                chat_id,
                data,
                caption=self.caption,
                reply_markup=self.markup,
                **self.options
            )


class VideoResponse(FileResponseBase):

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        with self.request_buffer() as data:
            return bot.send_video(
                chat_id,
                data,
                caption=self.caption,
                reply_markup=self.markup,
                **self.options
            )


class DocumentResponse(FileResponseBase):

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        with self.request_buffer() as data:
            return bot.send_document(
                chat_id,
                data,
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
        assert isinstance(bot, TeleBot)
        return bot.edit_message_text(
            self.message.text,
            chat_id,
            self.message_id,
            parse_mode=self.message.parse_mode,
            reply_markup=self.markup,
            **self.options
        )


class MarkupUpdate(MarkupResponseBase):

    def __init__(self, message_id, **options):
        assert message_id is not None
        super(MarkupUpdate, self).__init__(**options)
        self.message_id = message_id

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        return bot.edit_message_reply_markup(
            chat_id,
            self.message_id,
            reply_markup=self.markup,
            **self.options
        )


class ChatAction(ResponseBase):

    def __init__(self, action):
        """
        :param action:  One of the strings: 'typing', 'upload_photo',
        'record_video', 'upload_video', 'record_audio', 'upload_audio',
        'upload_document', 'find_location'.
        """
        super(ChatAction, self).__init__()
        self.action = action

    def send_to(self, bot, chat_id):
        assert isinstance(bot, TeleBot)
        return bot.send_chat_action(chat_id, self.action)


class ResponsePropagation(Exception):

    def __init__(self, response, *args):
        super(ResponsePropagation, self).__init__(*args)
        self.response = response


def prepare_response(response):
    if isinstance(response, list):
        return map(prepare_single_response, response)

    return [prepare_single_response(response)]


def prepare_single_response(response):
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

        if isinstance(response[0], bytes):
            props['data'] = response[0]

            if res_len > 1:
                if isinstance(response[1], (list, tuple)):
                    props['markup'] = prepare_markup(response[1])

                if isinstance(response[1], str):
                    props['caption'] = response[1]
                    if res_len > 2 and isinstance(response[2], (list, tuple)):
                        props['markup'] = prepare_markup(response[2])

            return PhotoResponse(**props)
