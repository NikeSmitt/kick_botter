from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['user'])
def get_group_user_info(message):
    """
    Команда позволяет получить данные о пользователе
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
        username = message.text.split()[1:][0]
        print(username)
    except ValueError:
        print('Ошибка формата команды group')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /user username')
        return
    
    telegram_user_id = db.get_telegram_user_id(username)
    user = db.get_user_info(telegram_user_id)
    if user:
        print(user)
        message_list = [f'Имя - {user[0]}']
        if user[1]:
            message_list.append(f'Фамилия - {user[1]}')
        if user[2]:
            message_list.append(f'Username - {user[2]}')
        
        is_group_admin = db.is_group_admin(telegram_user_id)
        
        # message_list.append(f'Root - {"ДА" if user[3] else "НЕТ"}')
        # message_list.append(f'Bash scripts - {"ДА" if user[4] else "НЕТ"}')
        # message_list.append(f'Group Admin - {"ДА" if is_group_admin else "НЕТ"}')
        
        if user[3]:
            message_list.append(f'Root - {"ДА" if user[3] else "НЕТ"}')
        else:
            message_list.append(f'Root - НЕТ')
            message_list.append(f'Bash scripts - {"ДА" if user[4] else "НЕТ"}')
            message_list.append(f'Group Admin - {"ДА" if is_group_admin else "НЕТ"}')
        
        message_to_send = '\n'.join(message_list)
        
        bot.send_message(message.from_user.id, message_to_send)
    else:
        bot.send_message(message.from_user.id, 'Данный пользователь не сохранен')
