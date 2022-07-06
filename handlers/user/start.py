from MySQLHandler import MySQLHandler
from bot import bot, cool_logger


@bot.message_handler(commands=['start'])
def started(message):
    db = MySQLHandler()
    
    # logging
    cool_logger.debug(f'Пользователь {message.from_user.username} c id {message.from_user.id} дал команду <start>')
    
    # проверяем, что команда запущена не из группого чата и он не бот
    if not str(message.chat.id).startswith('-') and not message.from_user.is_bot:
        bot.send_message(message.chat.id, f"Приятно познакомиться с Вами, {message.from_user.first_name}")
        
        # Сохраняем user в бд
        if db.save_user(
                message.from_user.id,
                message.from_user.first_name,
                message.from_user.last_name,
                message.from_user.username
        ):
            cool_logger.debug(
                f'Пользователь {message.from_user.username} c id {message.from_user.id} сохранен в бд')
            
            # сохраняем чат user с ботом в бд
            db.save_bot_user_chat(message.from_user.id, message.chat.id)
            
            cool_logger.info(
                f'Чат id {message.chat.id} c user {message.from_user.username} сохранен в бд')
        else:
            if db.update_user(
                    message.from_user.id,
                    message.from_user.first_name,
                    message.from_user.last_name,
                    message.from_user.username
            ):
                cool_logger.debug(
                    f'Данные пользователя {message.from_user.username} c id {message.from_user.id} обновлены в бд')
        
        bot.send_message(message.chat.id, "Ваши контактные данные сохранены. Спасибо")
    
    else:
        bot.send_message(message.chat.id,
                         "Используйте команду /start в личном чате с ботом, "
                         "выйдете из группы и зайдите в нее снова")
