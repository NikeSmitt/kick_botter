from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from handlers.helpers import is_root
from utils import create_time_stamp


@bot.message_handler(commands=['wipe_user'])
def wipe_user(message):
    """
    Выполняет wipe для конкретного пользователя
    :param message:
    :return:
    """
    
    cool_logger.info('Инициирование wipe_user метода')
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not is_root(message, db, cool_logger, bot):
        return
    
    # получаем имя пользователя
    try:
        username = ' '.join(message.text.split()[1:])
    except ValueError:
        cool_logger.error('Ошибка формата команды wipe_user')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /wipe_user username')
        return
    
    # получаем id телеги у пользователя
    
    telegram_user_id = db.get_telegram_user_id(username)
    if telegram_user_id is None:
        cool_logger.error(f'Пользователь {username} не найден в бд')
        bot.send_message(message.chat.id, f'Пользователь {username} не найден в бд')
        return
    
    # список групп, в которых пользователь забанен
    banned_group_names = []
    
    # получаем список всех групп, в которых есть пользователь
    
    user_groups = db.get_user_groups(telegram_user_id)
    for telegram_group_id, group_name in user_groups:
        
        # баним пользователя в группе
        
        try:
            bot.ban_chat_member(
                chat_id=telegram_group_id,
                user_id=telegram_user_id,
                until_date=create_time_stamp(days=367)
            )
            cool_logger.info(f'Пользователь {username} забанен в группе {group_name}')
            
            # сохраняем успешное забанивание в группе
            banned_group_names.append(group_name)
        
        except Exception as e:
            cool_logger.error(e)
        
        else:
            if db.update_group_user_kicked(telegram_group_id, telegram_user_id, kicked=True):
                cool_logger.debug(f'Обновление параметра пользователя kicked=True в бд'
                                  f'в группе {group_name}')
            else:
                cool_logger.error(f'Ошибка обновления kicked = True '
                                  f'у пользователя {username} в группе {group_name}')
    
    info_mes = f"Выполнена команда 'wipe_user' для {username} в {len(banned_group_names)} групп(ах)"
    cool_logger.info(info_mes)
    bot.send_message(message.from_user.id, info_mes)
