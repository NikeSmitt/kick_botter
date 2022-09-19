import telebot
from telebot import StateMemoryStorage

from MySQLHandler import MySQLHandler
from logs import log_config
import config
from filters.is_root import RootOnlyFilter

bot = telebot.TeleBot(config.TOKEN)
bot.add_custom_filter(RootOnlyFilter(bot))

import handlers
