from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['del_group'])
def del_group(message):
    db = MySQLHandler()
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение команды del_group')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    try:
        group_name = ' '.join(message.text.split()[1:])
    except ValueError:
        print('Ошибка формата команды del_group')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /del_group group_name')
        return
    
    # Получаем шв группы в телеге
    telegram_group_id = db.get_db_group_id(telegram_group_name=group_name)
    
    if telegram_group_id is None:
        bot.send_message(message.chat.id, 'Данная группа не сохранена')
        return

    # Получаем список пользователей
    group_users = db.get_group_users(group_name)
    for telegram_user_id, first_name, last_name, username in group_users:
        try:
            # баним пользователя навсегда, чтобы удалить его из чата
            bot.ban_chat_member(telegram_group_id, telegram_user_id, create_time_stamp(days=367))
        except Exception as err:
            cool_logger.error(f'Ошибка при попытке забанить пользователя {username} в группе {group_name}')
            cool_logger.error(err)
            bot.send_message(message.chat.id,
                             f'Ошибка при попытке забанить пользователя {username} в группе {group_name}')
    
    # Удаляем группу
    if db.delete_group(telegram_group_name=group_name):
        cool_logger.info(f'Группа {group_name} удалена')
        bot.send_message(message.chat.id, f'Группа {group_name} удалена')
    else:
        bot.send_message(message.chat.id, 'Ошибка удаления группы (см логи)')
        
