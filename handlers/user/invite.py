import json

import requests

import config
from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['invite'])
def invite_user(message):
    """
    Команда «invite» (invite user_id group_id) высылает указанному юзеру ссылку-инвайт в ЛС на указанную группу.
    :param message:
    :return:
    """
    print("Команда /invite")
    
    db = MySQLHandler()
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    try:
        spam = message.text.split()[1:]
        if not spam:
            raise ValueError
        group_name = ' '.join(spam[:-1])
        username = spam[-1]
    except ValueError:
        print('Ошибка формата команды invite')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /invite groupname username')
        return
    
    invite_link = db.get_last_invite_link(telegram_group_name=group_name)
    telegram_group_id = db.get_telegram_group_id(group_name)
    telegram_user_id = db.get_telegram_user_id(username)
    
    if not (telegram_group_id and telegram_user_id):
        bot.send_message(message.chat.id, 'Пользователь или группа не найдены')
        return
    
    if not invite_link:
        
        try:
            # так как в бд нет ссылки, необходимо создать экспортную новую ссылку
            new_export_invite_link = bot.export_chat_invite_link(telegram_group_id)
            cool_logger.debug(f'Создана инвайт ссылка для группы {group_name}')
        except Exception as err:
            cool_logger.error(f'Ошибка создания инвайт ссылки для группы {group_name}')
        else:
            db.save_last_invite_link(new_export_invite_link, telegram_group_id)
    
    expire_date = create_time_stamp(days=100)
    #
    url = f"https://api.telegram.org/bot{config.TOKEN}/createChatInviteLink?chat_id={telegram_group_id}&expire_date={expire_date}"
    
    # запрос
    req = requests.request("GET", url)
    
    # делаем json и забераем ссылку
    json_response = json.loads(req.text)
    
    new_invite_link = json_response['result']['invite_link']
    
    # bot.ban_chat_member(telegram_group_id, telegram_user_id)
    bot.unban_chat_member(telegram_group_id, telegram_user_id)
    bot.send_message(telegram_user_id, f"{group_name}\n{new_invite_link}")
    bot.send_message(message.from_user.id, f"Пользователю {username} отправлена ссылка")
