from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['del_admin'])
def set_del_admin_for_groups(message):
    """
    Команда удаляет права администратора «Группы» у пользователей
    :param message:
    :return:
    """
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    try:
        spam = message.text.split()[1:]
        group_name = ' '.join(spam[:-1])
        username = spam[-1]
    except ValueError:
        print('Ошибка формата команды invite')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /del_admin groupname username')
        return
    
    telegram_group_id = db.get_telegram_group_id(group_name)
    telegram_user_id = db.get_telegram_user_id(username)
    
    if not (telegram_group_id and telegram_user_id):
        bot.send_message(message.chat.id, 'Пользователь или группа не найдены')
        return
    
    db.update_user_in_group_admin(telegram_group_id, telegram_user_id, False)
    bot.send_message(message.chat.id, f'Пользователь {username} теперь НЕ админ группы {group_name}')
