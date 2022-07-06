import telebot

from MySQLHandler import MySQLHandler


# class IsRoot(telebot.custom_filters.SimpleCustomFilter):
#     key = 'is_root'
#
#     @staticmethod
#     def check(message: telebot.types.Message) -> bool:
#         db = MySQLHandler()
#         return db.is_root(message.from_user.id)
