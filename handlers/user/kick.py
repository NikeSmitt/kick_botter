from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['kick'])
def kick_user(message):
    """
    Команда «kick» (например, 'kick user_id group_id' ) удаляет пользователя из указанной «Группы».
    :param message:
    :return:
    """
    
    print("Команда /kick")
    
    try:
        spam = message.text.split()[1:]
        group_name = ' '.join(spam[:-1])
        username = spam[-1]
    except ValueError:
        print('Ошибка формата команды invite')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /kick groupname username')
        return
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    telegram_group_id = db.get_telegram_group_id(group_name)
    telegram_user_id = db.get_telegram_user_id(username)
    
    if not (telegram_group_id and telegram_user_id):
        bot.send_message(message.chat.id, 'Пользователь или группа не найдены')
        return
    
    if not db.is_group_admin_for_group(telegram_group_id, message.from_user.id) and not db.is_root(
            message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    try:
        # баним пользователя навсегда, чтобы удалить его из чата
        bot.ban_chat_member(telegram_group_id, telegram_user_id, create_time_stamp(days=367))
        # bot.unban_chat_member(telegram_group_id, telegram_user_id)
    except Exception as err:
        cool_logger.error(f'Ошибка при попытке забанить пользователя {username} в группе {group_name}')
        cool_logger.error(err)
        bot.send_message(message.chat.id, f'Ошибка при попытке забанить пользователя {username} в группе {group_name}')
        # удаляем пользователя из группы в бд
        # db.delete_user_in_group(telegram_group_id, telegram_user_id)
    
    else:
        
        # db.update_group_user_kicked(telegram_group_id, telegram_user_id, kicked=True)
        bot.send_message(message.chat.id, f'Пользователь {username} удален из группы {group_name} в ТГ')
    
    finally:
        # удаляем пользователя из группы в бд
        db.delete_user_in_group(telegram_group_id, telegram_user_id)
        bot.send_message(message.chat.id, f'Пользователь {username} удален из группы {group_name} в бд')
