import telebot
from telebot import AdvancedCustomFilter, types
from MySQLHandler import MySQLHandler


class RootOnlyFilter(AdvancedCustomFilter):
    key = 'for_root'
    
    def __init__(self, bot):
        self._bot: telebot.TeleBot = bot
    
    def check(self, message: types.Message, text):
        db = MySQLHandler()
        if not db.is_root(message.from_user.id):
            self._bot.reply_to(message, f'У вас нет прав на выполнение данной команды ({message.text})')
            return False
        return True
