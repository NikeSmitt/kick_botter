import json
import time

import requests

import config
from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['revert'])
def revert_users(message):
    """
    Команда «revert»: Бот генерирует для всех «Групп» пригласительные ссылки и
    рассылает их в ЛС пользователям с параметром БД «Kick»-«yes».
    После вступления в «Группу» запись пользователя в рамках «Группы» в БД на сервере удаляется.
    Если по истечению срока 7 дней пользователь не вступил в «Группу» то запись пользователя в рамках
    «Группы» в БД на сервере удаляется.
    :param message:
    :return:
    """
    # создаем инвайт ссылки для групп
    db = MySQLHandler()
    
    # для установки time.sleep
    telebot_api_count = 1
    REPEATS = 30
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    groups_id = db.get_all_groups()
    all_groups = 0
    all_users = 0
    for group_id in groups_id:
        
        # засыпаем после отправки необходимого количества запросов и обновляем счетчик
        if telebot_api_count % REPEATS == 0:
            time.sleep(1)
        
        telebot_api_count += 1
        
        # проверяем, что существует инвайт линк
        export_invite_link = db.get_last_invite_link(group_id)
        cool_logger.debug(f'Получена инвайт ссылка из бд для группы {group_id}')
        
        if not export_invite_link:
            # Создаем основную ссылку для приглашения в группу
            try:
                export_chat_invite_link = bot.export_chat_invite_link(group_id)
                cool_logger.debug(f'Создана инвайт ссылка для группы {group_id}')
            
            except Exception as err:
                cool_logger.error(f'Ошибка создания инвайт ссылки для группы {group_id}')
                cool_logger.error(f'{err}')
            
            else:
                # Сохраняем инвайт ссылку
                db.save_last_invite_link(export_chat_invite_link, group_id)
        
        # получаем всех пользователей в данной группе из бд
        users_in_groups = db.get_users_in_group(group_id)
        
        # добавляем только те группы, в которых есть пользователи
        all_groups += 1 if users_in_groups else 0
        
        # создаем дату, которой будет действовать ссылка
        expire_date = create_time_stamp(days=7)
        
        # получаем имя группы
        group_name = db.get_group_name(group_id)
        
        # создаем ссылку
        url = f"https://api.telegram.org/bot{config.TOKEN}/createChatInviteLink?chat_id={group_id}&expire_date={expire_date}"
        
        # запрос
        req = requests.request("GET", url)
        
        # делаем json и забераем ссылку
        json_response = json.loads(req.text)
        
        # отпрявляем ссылку в группу
        if 'result' in json_response and 'invite_link' in json_response['result']:
            new_invite_link = json_response['result']['invite_link']
            cool_logger.debug(f'Создана новая инвайт ссылка для группы {group_name}')
        else:
            cool_logger.error(f'Ошибка создания новой инвайт ссылки для группы {group_name}')
            continue
        
        for user_id in users_in_groups:
            
            _, _, username, *_ = db.get_user_info(user_id)
            # проверяем, что только кикнутые пользователи получат ссылки
            if db.is_user_in_group_kicked(group_id, user_id):
                try:
                    # сначала разбаниваем пользователя
                    bot.unban_chat_member(group_id, user_id, only_if_banned=True)
                
                except Exception as err:
                    cool_logger.error(f'Ошибка разбана пользователя {username} для группы {group_name}')
                    cool_logger.error(err)
                
                else:
                    # если все успешно, то увеличиваем счетчик
                    all_users += 1
                    # отправляем ссылку
                    bot.send_message(user_id, f"{group_name}\n{new_invite_link}")
                    
                    # удаляем пользователя из группы в бд
                    if db.delete_user_in_group(group_id, user_id):
                        cool_logger.debug(f'Пользователь {username} удален из группы {group_name}')
                    else:
                        cool_logger.error(f'Ошибка удаления пользователя {username} из группы {group_name}')
    
    info_mes = f"Выполнена команда 'revert' для {all_users} пользователь(ей) / {len(groups_id)} групп(ы)"
    bot.send_message(message.from_user.id, info_mes)
