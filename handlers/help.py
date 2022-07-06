from MySQLHandler import MySQLHandler
from bot_loader import bot


@bot.message_handler(commands=['help'])
def get_help(message):
    if not str(message.chat.id).startswith('-'):
        
        db = MySQLHandler()
        
        # проверяем права пользователя
        if db.is_root(message.from_user.id):
            help_messages = [
                "add_group - Добавить группу в бд",
                "wipe - Удалить всех пользователей",
                "revert - Вернуть всех пользователей",
                "wipe_group - Удалить всех пользователей в группе Формат: wipe_group groupname",
                "revert_group - Вернуть всех пользователей в группе Формат: revert_group groupname",
                "wipe_user - Удалить пользователя из всех групп Формат: wipe_user username",
                "revert_user - Вернуть пользователя в группы Формат: revert_user username",
                "invite - Формат: invite group_name username",
                "kick - Формат: kick group_name username",
                "set_admin - Формат: set_admin group_name username",
                "del_admin - Формат: del_admin group_name username",
                "group - Информация о группе Формат: group group_name",
                "user - Информация о пользователе Формат: user username",
                "del_user - Формат: del_user username",
                "del_group - Формат: del_group group_name",
                "get_stat - Получить статистику",
                "run - Формат: run file.sh",
                "logs - Получить файл логов Формат: logs 31-12-2001",
            ]
            help_message = '\n'.join(help_messages)
            bot.send_message(message.chat.id, help_message)
