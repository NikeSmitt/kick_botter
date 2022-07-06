import telebot

from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from handlers.helpers import is_root, get_invite_link


@bot.message_handler(commands=['revert_user'])
def revert_user(message: telebot.types.Message):
    """
    Команда для выполнения revert для конкретного пользователя в
    :param message: telebot.types.Message
    :return:
    """
    
    cool_logger.info('Иницирование revert_user метода')
    
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
    
    # список групп, ссылки на которые отправятся пользователю
    
    reverted_group_names = []
    
    # получаем список групп, в которых есть пользователь и он кикнут
    
    user_groups = db.get_user_groups(telegram_user_id, kicked=True)
    
    for telegram_group_id, group_name in user_groups:
        
        new_invite_link = get_invite_link(bot, db, telegram_group_id, group_name)
        
        if new_invite_link is None:
            cool_logger.error(f'Ошибка создания инвайт-ссылки для группы {group_name}')
            continue
        
        try:
            # разбаниваем пользователя
            bot.unban_chat_member(telegram_group_id, telegram_user_id, only_if_banned=True)
            
            # отправляем ссылку
            bot.send_message(
                chat_id=telegram_user_id,
                text=f'{group_name}\n{new_invite_link}'
                )
            
            reverted_group_names.append(username)
        
        except Exception as e:
            cool_logger.error(f'Ошибка разбана пользователя {username} в группе {group_name}')
            cool_logger.error(e)
            
        # удаляем пользователя из группы в бд
        if db.delete_user_in_group(telegram_group_id, telegram_user_id):
            cool_logger.debug(f'Пользователь {telegram_user_id} удален из группы {group_name}')
        else:
            cool_logger.error(f'Ошибка удаления пользователя {telegram_user_id} из группы {group_name}')
            
    info_mes = f"Выполнена команда 'revert_user' для пользователя {username}\n" \
               f"Отправлены ссылки для {len(reverted_group_names)} групп"
    
    bot.send_message(message.from_user.id, info_mes)
    
    