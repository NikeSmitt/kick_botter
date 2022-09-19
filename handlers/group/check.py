from telebot.apihelper import ApiTelegramException

from MySQLHandler import MySQLHandler
from bot import cool_logger
from bot_loader import bot
from telebot.types import Message


@bot.message_handler(commands=['check'], for_root=True)
def check_group(message: Message):
    """Запускает проверку количества пользователей в группах в бд и telegram"""
    db = MySQLHandler()
    # получаем список всех групп в бд
    all_groups_in_db = db.get_all_groups()
    
    # собираем список картежей с названием групп
    output = []
    
    for group_id in all_groups_in_db:
        telegram_group_name = db.get_group_name(group_id)
        try:
            # получаем количество пользователей в тг группе, без учета самого бота
            telegram_member_count = bot.get_chat_member_count(group_id) - 1
            
            # print(f'Количество пользователей в группе {telegram_group_name} - {telegram_member_count}')
        
        except ApiTelegramException as e:
            cool_logger.error(f"{telegram_group_name} - {e.result_json['description']}")
            output.append(f'Группы <b>{telegram_group_name}</b> не существует в ТГ')
            continue
        
        # смотрим сколько народу в группе в дб и они не кикнуты
        db_member_count = len(db.get_users_in_group(group_id, kicked=False))
        
        # если есть разница, то собираем строку
        if db_member_count != telegram_member_count:
            s = f'Группа <b>{telegram_group_name}</b> -> бд: {db_member_count} | тг: {telegram_member_count}'
            output.append(s)
    if len(output):
        bot.send_message(message.from_user.id, '\n'.join(output), parse_mode='html')
    else:
        bot.reply_to(message, 'Проверка пройдена нет')
