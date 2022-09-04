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
    print(all_groups_in_db)
    
    # собираем список картежей с названием групп
    output = []
    
    for group_id in all_groups_in_db:
        try:
            telegram_member_count = bot.get_chat_members_count(group_id)
            telegram_group_name = db.get_group_name(group_id)
            print(f'Количество пользователей в группе {telegram_group_name} - {telegram_member_count}')
        
        except Exception as e:
            print(e)
            cool_logger.error(f'Группы с id {group_id} не существует')
            continue
        
        # смотрим сколько народу в группе в дб и они не кикнуты
        db_member_count = len(db.get_users_in_group(group_id))
        
        # если есть разница, то собираем строку
        if db_member_count != telegram_member_count:
            s = f'Группа {telegram_group_name} в бд: {db_member_count} / в тг: {telegram_member_count}'
            output.append(s)
    
    bot.reply_to(message, '\n'.join(output))
