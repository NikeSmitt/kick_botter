import json
import time
from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from handlers.helpers import get_invite_link


@bot.message_handler(commands=['revert_group'])
def revert_users(message):
    db = MySQLHandler()
    
    # для установки time.sleep
    telebot_api_count = 1
    REPEATS = 30
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    # получаем имя группы
    try:
        group_name = ' '.join(message.text.split()[1:])
    except ValueError:
        print('Ошибка формата команды revert_group')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /revert_group group_name')
        return
    
    # счетчик пользователей
    reverted_users = 0
    
    # засыпаем после отправки необходимого количества запросов и обновляем счетчик
    if telebot_api_count % REPEATS == 0:
        time.sleep(1)
    
    telebot_api_count += 1
    
    # получаем id группы в телеге
    telegram_group_id = db.get_telegram_group_id(group_name)
    
    if telegram_group_id is None:
        cool_logger.error(f'Группа {group_name} не найдена в бд')
        bot.send_message(message.chat.id, f'Группа {group_name} не найдена в бд')
    
    # Получаем список пользователей в группе
    users_id_in_group = db.get_users_in_group(telegram_group_id, kicked=True)
    cool_logger.info(f'Происходит wipe_group в группе {group_name} ({len(users_id_in_group)} пользователей)')
    
    # получаем инвайт ссылку
    new_invite_link = get_invite_link(bot, db, telegram_group_id, group_name)
    
    if new_invite_link is None:
        cool_logger.error('Ошибка создания инвайт-ссылки')
        bot.send_message(message.from_user.id, 'Ошибка создания инвайт-сслыки')
        return
    
    for telegram_user_id in users_id_in_group:
        
        _, _, username, *_ = db.get_user_info(telegram_user_id)
        
        try:
            # сначала разбаниваем пользователя
            bot.unban_chat_member(telegram_group_id, telegram_user_id, only_if_banned=True)
            
            # отправляем ссылку
            bot.send_message(telegram_user_id, f"{group_name}\n{new_invite_link}")
            reverted_users += 1
        
        except Exception as err:
            cool_logger.error(f'Ошибка разбана пользователя {username} для группы {group_name}')
            cool_logger.error(err)
        
        # удаляем пользователя из группы в бд
        if db.delete_user_in_group(telegram_group_id, telegram_user_id):
            cool_logger.debug(f'Пользователь {username} удален из группы {group_name}')
        else:
            cool_logger.error(f'Ошибка удаления пользователя {username} из группы {group_name}')
    
    info_mes = f"Выполнена команда 'revert_group' для группы {group_name}. " \
               f"Ссылки отправлены {reverted_users} пользователям"
    bot.send_message(message.from_user.id, info_mes)
