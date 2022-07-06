from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['group'])
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
        group_name = ' '.join(message.text.split()[1:])
    except ValueError:
        print('Ошибка формата команды group')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /group group_name')
        return
    
    telegram_group_id = db.get_telegram_group_id(group_name)
    
    if telegram_group_id:
        users = db.get_group_users(group_name)
        bot.send_message(
            message.from_user.id,
            f"В группе id: {telegram_group_id}\nимя: {group_name}\nпользователей:  {len(users)}"
        )
    else:
        bot.send_message(message.from_user.id, 'Данная группа не сохранена')
