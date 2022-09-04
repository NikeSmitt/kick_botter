import telebot
from telebot import AdvancedCustomFilter, types

from MySQLHandler import MySQLHandler


class RootOnlyFilter(AdvancedCustomFilter):
    key = 'for_root'

    def __init__(self, bot):
        self._bot: telebot.TeleBot = bot
        self.db = MySQLHandler()
    
    def check(self, message: types.Message, text):
        if not self.db.is_root(message.from_user.id):
            self._bot.reply_to(message, f'У вас нет прав на выполнение данной команды ({message.text})')
            return False
        return True
