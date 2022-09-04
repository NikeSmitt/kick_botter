from datetime import datetime
import time

from telebot.apihelper import ApiTelegramException

from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['wipe'], for_root=True)
def wipe_users(message):
    """
    Команда «wipe»: Бот собирает актуальный список пользователей в каждой
    «Группе» и записывает их в БД на сервере, итерационно проходит по всем
    «Группам», удаляет оттуда всех пользователей и прописывает в БД в параметре
    «Kick» «yes».
    :param message: Message
    :return: None
    """
    cool_logger.info('Инициирование WIPE метода')
    
    db = MySQLHandler()
    
    # для установки time.sleep
    telebot_api_count = 1
    REPEATS = 30
    
    # список всех групп в базе
    groups = db.get_all_groups()
    
    # счетчики групп и пользователей, которых удалили
    all_groups = 0
    all_users = 0
    
    # собираем все ошибки "когда действие не 200 ОК"
    errors_for_user = []
    
    
    for group_id in groups:
        
        # логирование
        group_name = db.get_group_name(group_id)
        users_id_in_group = db.get_users_in_group(group_id)
        cool_logger.debug(f'Происходит WIPE в группе {group_name} ({len(users_id_in_group)} пользователей)')
        
        # считаем только те группы, в которых есть пользователи
        all_groups += 1 if users_id_in_group else 0
        
        for user_id in users_id_in_group:
            
            _, _, username, *_ = db.get_user_info(user_id)
            # создаем дату через год от текущего дня, чтобы забанить навсегда
            next_year = create_time_stamp(days=367)
            
            # засыпаем после отправки необходимого количества запросов
            if telebot_api_count % REPEATS == 0:
                time.sleep(1)
            
            telebot_api_count += 1
            
            # Тут особенность, доступна только функции ban и unban -> кикать мы не можем, поэтому сначала баним
            # навсегда, потом разбаним и пользователь удаляется из группы и сможет снова войти в группу по invite ссылке
            
            try:
                chat_member = bot.get_chat_member(group_id, user_id)
            except ApiTelegramException as err:
                cool_logger.error(f'Ошибка получения пользователя {username} из группы {group_name} в телеге')
                cool_logger.error(err)
                
                t = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                group = db.get_group_name(group_id)
                errors_for_user.append(f'{t} / {group} / {username} / {err.result_json["description"]}')
            else:
                # счетчик кикнутых пользователей
                all_users += 1
                
                # проверяем, что пользователь не менял свой username
                user_info = db.get_user_info(user_id)
                
                if user_info[2] != chat_member.user.username:
                    db.update_user(
                        user_id,
                        chat_member.user.first_name,
                        chat_member.user.last_name,
                        chat_member.user.username
                    )
            
            try:
                
                bot.ban_chat_member(group_id, user_id, next_year)
                # db.update_user_kicked(user_id, kicked=True)
                # bot.unban_chat_member(group_id, user_id)
            except ApiTelegramException as err:
                cool_logger.error(f'ОШИБКА! Попытка кикнуть пользователя {username} из группы {group_name}')
                cool_logger.error(err)

                t = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                group = db.get_group_name(group_id)
                errors_for_user.append(f'{t} / {group} / {username} / {err.result_json["description"]}')
            
            else:
                if db.update_group_user_kicked(group_id, user_id, kicked=True):
                    cool_logger.debug(f'Данные пользователя {username} (kicked) в таблице users_in_groups обновлены')
    
    info_mes = f"Выполнена команда 'wipe' - из {len(groups)} групп(ы) удалено {all_users} " \
               f"пользователь(ей) "

    bot.send_message(message.from_user.id, info_mes)
    
    # собираем сообщение с ошибками
    error_mes = '\n'.join(errors_for_user)
    bot.send_message(message.from_user.id, error_mes)

