import time

from MySQLHandler import MySQLHandler
from bot import bot, cool_logger
from utils import create_time_stamp


@bot.message_handler(commands=['wipe_group'])
def wipe_users(message):
    """
    Команда «wipe_group»: Получает список всех некикнутых пользователей в группе и
    банит их в группе
    :param message: Message
    :return: None
    """
    cool_logger.info('Инициирование wipe_group метода')
    
    db = MySQLHandler()
    
    # для установки time.sleep
    telebot_api_count = 1
    REPEATS = 30
    
    # print(message.chat.id)
    
    # проверяем права пользователя
    if not db.is_root(message.from_user.id):
        print(f'У пользователя {message.from_user.id} нет прав на выполнение данной команды')
        bot.send_message(message.chat.id, 'У вас нет прав на выполнение данной команды')
        return
    
    # получаем имя группы
    try:
        group_name = ' '.join(message.text.split()[1:])
    except ValueError:
        print('Ошибка формата команды wipe_group')
        bot.send_message(message.chat.id, 'Неправильный формат команды. Формат: /wipe_group group_name')
        return
    
    # счетчики групп и пользователей, которых удалили
    kicked_users_count = 0
    
    # логирование
    telegram_group_id = db.get_telegram_group_id(group_name)
    if telegram_group_id is None:
        cool_logger.error(f'Группа {group_name} не найдена в бд')
        bot.send_message(message.chat.id, f'Группа {group_name} не найдена в бд')
    
    # Получаем список пользователей в группе
    users_id_in_group = db.get_users_in_group(telegram_group_id, kicked=False)
    cool_logger.info(f'Происходит wipe_group в группе {group_name} ({len(users_id_in_group)} пользователей)')
    
    for telegram_user_id in users_id_in_group:
        
        # создаем дату через год от текущего дня, чтобы забанить навсегда
        next_year = create_time_stamp(days=367)
        
        # засыпаем после отправки необходимого количества запросов
        if telebot_api_count % REPEATS == 0:
            time.sleep(1)
        
        telebot_api_count += 1
        
        # получаем данные пользователя из бд для проверки
        user_info = db.get_user_info(telegram_user_id)
        saved_user_name = user_info[2]
        
        # получаем данные пользователя из телеги, чтобы обновить данные
        try:
            chat_member = bot.get_chat_member(telegram_group_id, telegram_user_id)
        except Exception as err:
            cool_logger.error(f'Ошибка получения пользователя {telegram_user_id} из группы {group_name} в телеге')
            cool_logger.error(err)
        else:
            
            # проверяем, что пользователь не менял свой username
            if user_info[2] != chat_member.user.username:
                db.update_user(
                    telegram_user_id,
                    chat_member.user.first_name,
                    chat_member.user.last_name,
                    chat_member.user.username
                )
        
        try:
            bot.ban_chat_member(telegram_group_id, telegram_user_id, next_year)
            # счетчик кикнутых пользователей
            kicked_users_count += 1
        except Exception as err:
            cool_logger.error(f'ОШИБКА! Попытка кикнуть пользователя {saved_user_name} из группы {telegram_group_id}')
            cool_logger.error(err)
        
        else:
            if db.update_group_user_kicked(telegram_group_id, telegram_user_id, kicked=True):
                cool_logger.debug(f'Данные пользователя {telegram_user_id} (kicked) в таблице users_in_groups обновлены')
    
    info_mes = f"Выполнена команда 'wipe_group' - из группы {group_name} удалено {kicked_users_count} " \
               f"пользователь(ей) "
    cool_logger.info(info_mes)
    bot.send_message(message.from_user.id, info_mes)


if __name__ == '__main__':
    db = MySQLHandler()
    group_id = db.get_telegram_group_id('test_kickbot_group_1')
    print(group_id)
    print(db.get_users_in_group(group_id))
    