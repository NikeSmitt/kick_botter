import telebot
from logs import log_config
import config

bot = telebot.TeleBot(config.TOKEN)

import handlers
