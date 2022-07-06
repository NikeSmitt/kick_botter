from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(content_types=['new_chat_members', 'group_chat_created', 'migrate_to_chat_id', 'left_chat_member'])
def new_chat_member_added_to_group(message):
    new_chat_members = message.new_chat_members
    db = MySQLHandler()
    
    # для логов
    if new_chat_members:
        cool_logger.debug(f'Новые пользователи в группе {message.chat.title}:'
                          f' {[user.username for user in new_chat_members]}')
    
    if message.left_chat_member:
        
        # если бот ушел, то удаляем группу из бд
        if message.left_chat_member.is_bot:
            if db.delete_group(message.chat.id, message.chat.title):
                cool_logger.debug(f'Удалена группа {message.chat.title} из бд')
            else:
                cool_logger.debug(f'Ошибка удаления группы {message.chat.title} из бд')
        
        cool_logger.info(f'Пользователь {message.left_chat_member.username} вышел из группы {message.chat.title}')
    
    # сервисное сообщение об изменении id группы
    if message.migrate_to_chat_id:
        db.update_saved_group(message.migrate_to_chat_id, message.chat.title)
    
    # сервисное сообщение о новых пользовательях или о создании группы с ботом
    if new_chat_members or message.group_chat_created:
        
        # проверяем, что бот добавился в группу или создалась группа с ботом
        if message.group_chat_created or list(filter(lambda user: user.is_bot, new_chat_members)):
            if not db.is_group_saved(message.chat.id, message.chat.title):
                bot.send_message(message.chat.id, 'Необходимо зарегистрировать название группы в боте')
                bot.leave_chat(message.chat.id)
            else:
                db.update_saved_group(message.chat.id, message.chat.title)
        
        # бот уже в группе, значит нужно сохранять пользователей в данной группе, если они есть
        if new_chat_members:
            saved_chat_members = db.get_users_in_group(message.chat.id)
            for new_chat_member in new_chat_members:
                
                # если пользователь зарегистрирован и он не бот
                if not db.get_user_info(new_chat_member.id) and not new_chat_member.is_bot:
                    bot.send_message(message.chat.id, f'Пользователь {new_chat_member.username} не зарегистрирован')
                    cool_logger.error(f'Пользователь {new_chat_member.username} не зарегистрирован в боте')
                    return
                if new_chat_member not in saved_chat_members and not new_chat_member.is_bot:
                    
                    # проверяем, что пользователь не создатель группы
                    try:
                        chat_member = bot.get_chat_member(message.chat.id, new_chat_member.id)
                        # print(chat_member)
                    except Exception as err:
                        cool_logger.error(f'Ошибка получения пользователя {new_chat_member.username} '
                                          f'из группы {message.chat.id} в телеге')
                        cool_logger.error(err)
                    else:
                        if chat_member.status in ['creator']:
                            cool_logger.info(
                                f'В группу {message.chat.title} вошел создатель группы {new_chat_member.username}')
                            continue
                        
                        if db.save_user_in_group(message.chat.id, new_chat_member.id):
                            cool_logger.info(f'В группе {message.chat.title} '
                                             f'пользователь {new_chat_member.username} сохранен в бд')

