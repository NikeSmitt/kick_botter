from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['add_group'])
def add_group(message):
    """
    Доваляем группу вручную
    :param message:
    :return:
    """
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        cool_logger.info(f'У пользователя {message.from_user.id} нет прав на выполнение команды add_group')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    try:
        group_name = ' '.join(message.text.split()[1:])
    except ValueError:
        print('Ошибка формата команды group')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /group group_name')
        return
    
    group_name = group_name.strip()
    if not group_name:
        bot.send_message(message.from_user.id, 'Неправильный формат команды. Формат: /group group_name')
        return
    
    if db.is_group_saved(telegram_group_title=group_name):
        bot.send_message(message.from_user.id, f'Группа {group_name} уже добавлена')
    else:
        if db.save_group(group_id=None, group_name=group_name):
            cool_logger.info(f'Группа {group_name}, в которой разрешено работать боту сохранена в бд ')
            
            bot.send_message(message.from_user.id, f'Группа {group_name}, в которой разрешено работать боту, добавлена')
