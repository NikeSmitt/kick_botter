from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['del_user'])
def del_user(message):
    db = MySQLHandler()
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    # парсим и проверяем формат команды
    try:
        username = message.text.split()[-1]
    except ValueError:
        print('Ошибка формата команды del_user')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /del_user username')
        return
    
    # ищем id телеги пользователя в бд по имени
    telegram_user_id = db.get_telegram_user_id(username)
    
    # не нашли
    if not telegram_user_id:
        bot.send_message(message.chat.id, 'Данный пользователь не сохранен')
        return
    
    # если пользователь оказался root
    # if db.is_root(telegram_user_id):
    #     bot.send_message(message.chat.id, f'Нельзя удалить пользователя {username} (root)')
    #     return
    
    # получаем все id групп пользователя
    user_groups = db.get_user_groups(telegram_user_id)
    
    for telegram_group_id, group_name in user_groups:
        
        try:
            # баним пользователя навсегда, чтобы удалить его из чата
            bot.ban_chat_member(telegram_group_id, telegram_user_id, create_time_stamp(days=367))
            # bot.unban_chat_member(telegram_group_id, telegram_user_id)
        except Exception as err:
            cool_logger.error(f'Ошибка при попытке забанить пользователя {username} в группе {group_name}')
            cool_logger.error(err)
            bot.send_message(message.chat.id,
                             f'Ошибка при попытке забанить пользователя {username} в группе {group_name}')
    
    db.delete_user(telegram_user_id)
    bot.send_message(message.chat.id, f'Пользователь {username} удален')
