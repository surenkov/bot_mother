from telebot import TeleBot
from telebot.types import *
from telebot.apihelper import ApiException


class Bot:
    def __init__(self, api_token: str):
        self.webhook_url = ''
        self.telebot = TeleBot(api_token)

    def init_hook(self, webhook_url: str):
        try:
            self._init_handlers()
            self.webhook_url = webhook_url
            return self.telebot.set_webhook(webhook_url)
        except ApiException:
            pass

    def handle_update(self, update: Update):
        self.telebot.process_new_updates([update])

    def _init_handlers(self):
        bot = self.telebot
        for command, func in self.commands().items():
            name = "" #TODO message handler
            bot.add_message_handler({
                'function': func,
                'filters': {'commands': {command}}
            })
            bot.add_message_handler({
                'function': func,
                'filters': {'func': lambda message, com_name=name :
                 message.text == com_name}
            })

        bot.add_message_handler({
            'function': self._process_text_message,
            'filters': {'content_types': {'text'}}
        })

        bot.add_message_handler({
            'function': self._process_photo,
            'filters': {'content_types': {'photo','document'}}
        })

    def _start_conversation(self, message: Message):
        pass

    def _process_text_message(self, message: Message):
        pass

    def _process_photo(self, message: Message):
        pass

    def _back_button(self, message: Message):
        pass

    def send_bot_message(self, bot_message, chat_id, extra_buttons=None,
                         hide_keyboard=False, inline_buttons=None):

        markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        if bot_message.responses is not None:
            for response in bot_message.responses:
                markup.add(KeyboardButton(response.text))

        if extra_buttons:
            for button in extra_buttons:
                markup.add(KeyboardButton(button))

        if hide_keyboard:
            markup = ReplyKeyboardRemove()
        if inline_buttons:
            markup = []
            for row in inline_buttons:
                inline_markup_row = []
                for button in row:
                    inline_markup_row.append(InlineKeyboardButton(text=button))
                markup.append(inline_markup_row)

        self.telebot.send_message(
            chat_id,
            str.strip(bot_message.text),
            reply_markup=markup,
            disable_web_page_preview=False,
        )

    def update_message(self, text, buttons, message_id):
        pass


    def commands(self):
        return {
                'start': self._start_conversation,
                'back': self._back_button,
        }
