from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['get_stat'])
def get_statistics(message):
    """
    Выводим статистику по боту
    :param message:
    :return:
    """
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    groups = len(db.get_all_groups())
    users = len(db.get_all_users())
    
    roots = db.get_root_count()
    admins = db.get_admin_count()
    
    mess = f"Количество групп: {groups}\n" \
           f"Пользователей: {users}\n" \
           f"Пользователей Root: {roots}\n" \
           f"Пользователей Group Admin: {admins}"
    
    bot.send_message(message.from_user.id, mess)
