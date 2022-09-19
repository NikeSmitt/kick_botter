import logging
from typing import Union, Optional

import mysql
import logs.log_config
from mysql.connector import connection, errorcode

from config import mysql_config

cool_logger = logging.getLogger('bot_logger')


class MySQLHandler:
    
    def __init__(self, config=mysql_config):
        try:
            self.connector = connection.MySQLConnection(**config)
            self.cursor = self.connector.cursor(buffered=True)
        
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                print('Database does not exist')
            else:
                print(err)
    
    def get_all_users(self):
        """
        Выводит все пользователей в базе
        :return:
        """
        
        self.cursor.reset()
        
        self.cursor.execute("SELECT * FROM users")
        return list(self.cursor)
    
    def get_all_groups(self):
        """
        Выводит все пользователей в базе
        :return:
        """
        
        self.cursor.reset()
        
        self.cursor.execute("SELECT group_id FROM bot_groups")
        all_groups = list(map(lambda value: value[0], list(self.cursor)))
        return all_groups
    
    def save_user(self, user_id, first_name=None, last_name=None, username=None):
        """
        Сохраняем данные пользователя
        :param username: str
        :param first_name: str
        :param last_name: str
        :param user_id: int
        :return: bool
        """
        
        self.cursor.reset()
        
        add_user = ("INSERT INTO users "
                    "(user_id, first_name, last_name, username) "
                    "VALUES (%s, %s, %s, %s)")
        data_user = (user_id, first_name, last_name, username)
        try:
            self.cursor.execute(add_user, data_user)
            self.connector.commit()
        
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                # print(f"Пользователь c id {user_id} уже сохранен")
                cool_logger.info(f"Пользователь c id {user_id} уже сохранен в бд")
            else:
                cool_logger.error(err)
            return False
        
        return True
    
    def update_user(self, telegram_id, first_name=None, last_name=None, username=None):
        """
        Обновление полей пользователя в бд
        :param telegram_id:
        :param first_name:
        :param last_name:
        :param username:
        :return: bool
        """
        
        sql_ = "UPDATE users SET first_name=%s, last_name=%s, username=%s WHERE user_id = %s"
        data_user = (first_name, last_name, username, telegram_id)
        
        try:
            self.cursor.execute(sql_, data_user)
            self.connector.commit()
        except mysql.connector.Error as err:
            cool_logger.error(err)
            return False
        return True
    
    def is_user_in_group_kicked(self, telegram_group_id: int, telegram_user_id: int) -> bool:
        """
        Проверяем, что пользователь имеет в поле kicked True
        :param telegram_group_id: int
        :param telegram_user_id: int
        :return: bool
        """
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        db_group_id = self.get_db_group_id(telegram_group_id)
        
        update_user = (
            "SELECT kicked FROM users_in_groups "
            "WHERE group_id = %s AND user_id = %s")
        
        data_user = (db_group_id, db_user_id)
        
        try:
            self.cursor.execute(update_user, data_user)
            self.connector.commit()
            # print('Данные пользователя (kicked) в таблице users_in_groups обновлены')
        except mysql.connector.Error as err:
            print(err)
        
        res = list(self.cursor)
        
        if res:
            return res[0][0]
        else:
            return False
    
    def update_user_kicked(self, telegram_user_id, kicked=False):
        """
        Обновляем запись kicked в таблице users
        :param telegram_user_id:
        :param kicked: bool
        :return: None
        """
        
        self.cursor.reset()
        
        update_user = (
            "UPDATE users "
            "SET kicked = %s "
            "WHERE user_id = %s")
        
        data_user = (kicked, telegram_user_id)
        try:
            self.cursor.execute(update_user, data_user)
            self.connector.commit()
            print('Данные пользователя (kicked) обновлены')
        except mysql.connector.Error as err:
            print(err)
        
        res = list(self.cursor)
        
        if res:
            return res[0][0]
        else:
            return False
    
    def update_group_user_kicked(self, telegram_group_id: int, telegram_user_id: int, kicked=False):
        """
        Обновляем запись в таблице users_in_groups в поле kicked
        :param kicked:
        :param telegram_group_id: int
        :param telegram_user_id: int
        :return:
        """
        db_user_id = self.get_db_user_id(telegram_user_id)
        db_group_id = self.get_db_group_id(telegram_group_id)
        
        update_user = (
            "UPDATE users_in_groups "
            "SET kicked = %s "
            "WHERE group_id = %s AND user_id = %s")
        
        data_user = (kicked, db_group_id, db_user_id)
        
        try:
            self.cursor.execute(update_user, data_user)
            self.connector.commit()
        
        except mysql.connector.Error as err:
            print(err)
            return False
        
        return True
    
    def get_telegram_group_id(self, group_name: str) -> Optional[int]:
        """
        Получить id группы в telegram
        :param group_name: str
        :return: int
        """
        self.cursor.reset()
        query = 'SELECT group_id FROM bot_groups WHERE group_name=%s'
        try:
            self.cursor.execute(query, (group_name,))
        except mysql.connector.Error as err:
            print('Ошибка получения telegram_group_id')
            print(err)
        
        group_id = list(self.cursor)
        
        if group_id:
            return group_id[0][0]
    
    def get_telegram_user_id(self, username: str) -> int:
        """
        Получить id группы в telegram
        :param username: str
        :return: int
        """
        self.cursor.reset()
        query = 'SELECT user_id FROM users WHERE username=%s'
        try:
            self.cursor.execute(query, (username,))
        except mysql.connector.Error as err:
            print('Ошибка получения telegram_user_id')
            print(err)
        
        user_id = list(self.cursor)
        
        if user_id:
            return user_id[0][0]
    
    def is_group_saved(self, telegram_group_id=None, telegram_group_title=None):
        """
        Проверяем наличие группы в БД
        :param telegram_group_title: str
        :param telegram_group_id: int
        :return: bool
        """
        self.cursor.reset()
        
        query = "SELECT id FROM bot_groups WHERE group_id = %s OR group_name = %s"
        
        try:
            self.cursor.execute(query, (telegram_group_id, telegram_group_title))
        except mysql.connector.Error as err:
            print(err)
        
        # print(self.cursor)
        return len(list(self.cursor)) > 0
    
    def update_saved_group(self, telegram_group_id, telegram_group_title):
        """
        Обновляем поля в сохраненных группах
        :param telegram_group_id:
        :param telegram_group_title:
        :return:
        """
        self.cursor.reset()
        
        update_group = ("UPDATE bot_groups "
                        "SET group_id = %s, group_name = %s "
                        "WHERE group_id = %s OR group_name = %s "
                        )
        
        data_group = (telegram_group_id, telegram_group_title, telegram_group_id, telegram_group_title)
        
        try:
            self.cursor.execute(update_group, data_group)
            self.connector.commit()
            cool_logger.debug(f'Данные группы {telegram_group_title} обновлены: id: {telegram_group_id}')
        
        except mysql.connector.Error as err:
            cool_logger.error(f'Ошибка обновления данных группы {telegram_group_title} id: {telegram_group_id}')
            cool_logger.error(err)
            return False
        
        return True
    
    def save_group(self, group_id=None, group_name=None):
        """
        Сохраняем группу в базе
        :param group_name: str
        :param group_id: int
        :return:
        """
        
        self.cursor.reset()
        
        # создаем фейковый id группы
        if not group_id:
            from random import random
            
            group_id = int(str(random())[2:10])
        
        add_group = ("INSERT INTO bot_groups (group_id, group_name) "
                     "VALUES (%s, %s)")
        data_group = (group_id, group_name)
        
        try:
            self.cursor.execute(add_group, data_group)
            self.connector.commit()
        
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                cool_logger.error(f"Группа <{group_name}> уже сохранена")
            else:
                cool_logger.error(err)
            return False
        
        return True
    
    def get_group_name(self, telegram_group_id: int) -> str:
        """
        Получаем имя группы
        :param telegram_group_id: int
        :return: str
        """
        self.cursor.reset()
        query = "SELECT group_name FROM bot_groups WHERE group_id=%s"
        
        try:
            self.cursor.execute(query, (telegram_group_id,))
        except mysql.connector.Error as err:
            print(err)
        
        user = list(self.cursor)
        if user:
            return user[0][0]
    
    def save_user_in_group(self, telegram_group_id, telegram_user_id):
        """
        Сохраняем user в таблицу в соответствии с группой, в которой он присутствует
        :param telegram_group_id: int
        :param telegram_user_id: int
        :return: None
        """
        
        self.cursor.reset()
        
        add_user_group = ("INSERT INTO users_in_groups (group_id, user_id) "
                          "VALUE (%s, %s)")
        data_user_group = (self.get_db_group_id(telegram_group_id), self.get_db_user_id(telegram_user_id))
        
        try:
            self.cursor.execute(add_user_group, data_user_group)
            self.connector.commit()
        
        except mysql.connector.Error as err:
            cool_logger.error(err)
            return False
        
        return True
    
    def get_users_in_group(self, telegram_group_id, kicked=None):
        """
        Получить текущий список всех пользователей в группе
        :param kicked:
        :param telegram_group_id: int
        :return:
        """
        self.cursor.reset()
        
        query = ("SELECT u.user_id FROM users_in_groups ug "
                 "JOIN users u on ug.user_id = u.id "
                 "JOIN bot_groups bg on ug.group_id = bg.id "
                 "WHERE bg.group_id = %s ")
        
        query_data = (telegram_group_id,)
        
        if kicked is not None:
            query += "AND ug.kicked=%s"
            query_data = (*query_data, kicked)
        
        try:
            self.cursor.execute(query, query_data)
        except mysql.connector.Error as err:
            print(err)
        
        return list(map(lambda query_set: query_set[0], self.cursor))
    
    def get_user_groups(self, telegram_user_id, kicked=None):
        """
        Получаем все telegram id групп, в которых есть пользователь
        :param kicked:
        :param telegram_user_id: int
        :return: List[int]
        """
        query = ("SELECT bg.group_id, bg.group_name FROM users_in_groups ug "
                 "JOIN bot_groups bg ON bg.id = ug.group_id "
                 "JOIN users u ON ug.user_id = u.id "
                 "WHERE u.user_id = %s")
        
        params = (telegram_user_id,)
        
        if kicked is not None:
            query = query + " AND ug.kicked = %s"
            params = (*params, kicked)
        try:
            self.cursor.execute(query, params)
        except mysql.connector.Error as err:
            cool_logger.error(err)
        
        return list(map(lambda query_set: query_set, self.cursor))
    
    def get_group_users(self, telegram_group_name):
        """
        Получаем список всех пользователей в группе
        :param telegram_group_name: str
        :return:
        """
        self.cursor.reset()
        
        query = 'SELECT id FROM bot_groups WHERE group_name = %s'
        
        try:
            self.cursor.execute(query, (telegram_group_name,))
        except mysql.connector.Error as err:
            print(err)
        
        db_group_id_list = list(self.cursor)
        if db_group_id_list:
            db_group_id = db_group_id_list[0][0]
        else:
            return
        
        query = ("SELECT u.user_id, first_name, last_name, username FROM users_in_groups ug "
                 "JOIN users u ON ug.user_id = u.id "
                 "WHERE group_id = %s")
        
        try:
            self.cursor.reset()
            self.cursor.execute(query, (db_group_id,))
        except mysql.connector.Error as err:
            print(err)
        
        return list(self.cursor)
    
    def delete_user_in_group(self, telegram_group_id, telegram_user_id):
        """
        Удаляет строку группа - пользователь из users_in_groups
        :param telegram_group_id: int
        :param telegram_user_id: int
        :return:
        """
        
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        db_group_id = self.get_db_group_id(telegram_group_id)
        
        delete_user = (
            "DELETE FROM users_in_groups "
            "WHERE group_id = %s AND user_id = %s")
        
        data_user = (db_group_id, db_user_id)
        
        try:
            self.cursor.execute(delete_user, data_user)
            self.connector.commit()
            self.cursor.reset()
        
        except mysql.connector.Error as err:
            print(err)
            return False
        return True
    
    def get_user_info(self, telegram_user_id):
        """
        Возвращает информацию о пользователе
        :param telegram_user_id:
        :return:
        """
        self.cursor.reset()
        
        query = ("SELECT first_name, last_name, username, "
                 "root, bash_execution FROM users WHERE user_id = %s")
        
        try:
            self.cursor.execute(query, (telegram_user_id,))
        except mysql.connector.Error as err:
            print(err)
        
        user = list(self.cursor)
        if user:
            return user[0]
    
    def delete_user(self, telegram_user_id):
        """
        Удалить пользователя из БД
        :param telegram_user_id:
        :return:
        """
        self.cursor.reset()
        try:
            self.cursor.execute('DELETE FROM users WHERE user_id= %s', (telegram_user_id,))
            self.connector.commit()
        except mysql.connector.Error as err:
            print(err)
    
    def delete_group(self, telegram_group_id=None, telegram_group_name="Noname"):
        """
        Удалить пользователя из БД
        :param telegram_group_name:
        :param telegram_group_id:
        :return:
        """
        self.cursor.reset()
        try:
            self.cursor.execute(
                'DELETE FROM bot_groups WHERE group_id=%s OR group_name=%s',
                (telegram_group_id, telegram_group_name)
            )
            self.connector.commit()
        except mysql.connector.Error as err:
            cool_logger.error(err)
            return False
        
        return True
    
    def save_bot_user_chat(self, telegram_user_id, telegram_chat_id):
        """
        Сохранить id приватного чата в базу в bot_user_private_chats
        :param telegram_user_id: int
        :param telegram_chat_id: int
        :return:
        """
        
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        
        add_user_id_chat_id = ("INSERT INTO bot_user_private_chats (user_id, telegram_chat_id) "
                               "VALUES (%s, %s)")
        
        data_user_id_chat_id = (db_user_id, telegram_chat_id)
        
        try:
            self.cursor.execute(add_user_id_chat_id, data_user_id_chat_id)
            self.connector.commit()
            # print('Приватный чат с ботом сохранен в БД')
            return True
        
        except mysql.connector.Error as err:
            print(err)
        return False
    
    def save_last_invite_link(self, invite_link, telegram_group_id: int):
        """
        Сохраняем последнюю созданную инвайт ссылку
        :param telegram_group_id:
        :param invite_link: str
        :return:
        """
        
        self.cursor.reset()
        db_group_id = self.get_db_group_id(telegram_group_id)
        self.cursor.reset()
        
        if self.get_last_invite_link(telegram_group_id):
            update_link = "UPDATE last_invite_link SET link= %s WHERE group_id =%s"
        else:
            update_link = "INSERT INTO last_invite_link (link, group_id) VALUES (%s, %s)"
        try:
            self.cursor.execute(update_link, (invite_link, db_group_id))
            self.connector.commit()
            
            cool_logger.debug(f'Инвайт ссылка для группы {telegram_group_id} обновлена')
        except mysql.connector.Error as err:
            cool_logger.error(f'Ошибка сохранения инвайт ссылки')
            cool_logger.error(err)
    
    def get_last_invite_link(self, telegram_group_id: int = 0, telegram_group_name='Noname'):
        """
        Получаем последнюю созданную инвайт ссылку
        :return:
        """
        
        self.cursor.reset()
        
        db_group_id = self.get_db_group_id(telegram_group_id, telegram_group_name)
        query = "SELECT link FROM last_invite_link WHERE group_id = %s"
        
        try:
            self.cursor.execute(query, (db_group_id,))
        except mysql.connector.Error as err:
            cool_logger.error(f'Ошибка получения инвайт ссылки для группы {telegram_group_name} из бд')
            cool_logger.error(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        # print(result)
        return result[0] if result else None
    
    def get_bot_user_chat_id(self, telegram_user_id):
        """
        Получить telegtam chat_id приватного общения user и бота
        :param telegram_user_id: int
        :return:
        """
        
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        
        quary = "SELECT telegram_chat_id FROM bot_user_private_chats WHERE user_id = %s"
        
        try:
            self.cursor.execute(quary, (db_user_id,))
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else -1
    
    def update_user_in_group_admin(self, telegram_group_id: int, telegram_user_id: int, is_admin=False):
        """
        Обновляем поле is_admin в users_in_groups
        :param is_admin: bool
        :param telegram_group_id: int
        :param telegram_user_id: int
        :return:
        """
        
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        db_group_id = self.get_db_group_id(telegram_group_id)
        
        update_user = (
            "UPDATE users_in_groups "
            "SET group_admin = %s "
            "WHERE user_id = %s AND group_id = %s")
        
        data_user = (is_admin, db_user_id, db_group_id)
        try:
            self.cursor.execute(update_user, data_user)
            self.connector.commit()
            print('Данные пользователя (is_admin) обновлены')
        except mysql.connector.Error as err:
            print(err)
    
    # def update_user_admin(self, telegram_user_id: int, is_admin=False):
    #     """
    #     Обновляем поле is_admin в users
    #     :param telegram_user_id: int
    #     :param is_admin: bool
    #     :return: bool
    #     """
    #     self.cursor.reset()
    #
    #     db_user_id = self.get_db_user_id(telegram_user_id)
    #
    #     update_user = (
    #         "UPDATE users "
    #         "SET group_admin = %s "
    #         "WHERE user_id = %s")
    #
    #     data_user = (is_admin, db_user_id)
    #     try:
    #         self.cursor.execute(update_user, data_user)
    #         self.connector.commit()
    #         print('Данные пользователя (is_admin) в users обновлены')
    #     except mysql.connector.Error as err:
    #         print(err)
    
    def get_db_group_id(self, telegram_group_id=0, telegram_group_name="Noname"):
        """
        Получить id группы в базе
        :param telegram_group_name: str
        :param telegram_group_id: int
        :return:
        """
        
        self.cursor.reset()
        
        query = "SELECT id FROM bot_groups WHERE group_id = %s OR group_name = %s"
        
        self.cursor.execute(query, (telegram_group_id, telegram_group_name))
        result = list(map(lambda query_set: query_set[0], self.cursor))
        if len(result):
            return result[0]
    
    def get_db_user_id(self, telegram_user_id):
        """
        Получить id user в базе
        :param telegram_user_id: int
        :return:
        """
        
        self.cursor.reset()
        
        query = "SELECT id FROM users WHERE user_id = %s"
        
        self.cursor.execute(query, (telegram_user_id,))
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else -1
    
    def is_root(self, telegram_user_id: int):
        """
        Проверяет наличие прав root у пользователя
        :param telegram_user_id:
        :return:
        """
        
        self.cursor.reset()
        
        query = "SELECT root FROM users WHERE user_id = %s"
        
        try:
            self.cursor.execute(query, (telegram_user_id,))
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else False
    
    def is_group_admin_for_group(self, telegram_group_id: int, telegram_user_id: int):
        """
        Праверяет наличие прав group_admin у пользователя
        :param telegram_group_id:
        :param telegram_user_id:
        :return:
        """
        
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        db_group_id = self.get_db_group_id(telegram_group_id)
        
        query = "SELECT group_admin FROM users_in_groups WHERE group_id = %s AND user_id = %s"
        
        try:
            self.cursor.execute(query, (db_group_id, db_user_id))
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else False
    
    def is_group_admin(self, telegram_user_id: int):
        """
        Праверяет наличие прав group_admin у пользователя
        :param telegram_user_id: int
        :return:
        """
        
        self.cursor.reset()
        
        db_user_id = self.get_db_user_id(telegram_user_id)
        
        query = "SELECT * FROM users_in_groups WHERE user_id= %s AND group_admin"
        
        try:
            self.cursor.execute(query, (db_user_id,))
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return True if result else False
    
    def can_run_scripts(self, telegram_user_id: int):
        """
        Праверяет наличие прав root у пользователя
        :param telegram_user_id:
        :return:
        """
        
        self.cursor.reset()
        
        query = "SELECT bash_execution FROM users WHERE user_id = %s"
        
        try:
            self.cursor.execute(query, (telegram_user_id,))
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else False
    
    def get_root_count(self):
        """
        Возвращает количество пользователей с правами root
        :return:
        """
        
        self.cursor.reset()
        
        query = 'SELECT COUNT(id) FROM users WHERE root'
        
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else False
    
    def get_admin_count(self):
        """
        Возвращает количество пользователей с правами root
        :return:
        """
        
        self.cursor.reset()
        
        query = 'SELECT COUNT(id) FROM users_in_groups WHERE group_admin'
        
        try:
            self.cursor.execute(query)
        except mysql.connector.Error as err:
            print(err)
        
        result = list(map(lambda query_set: query_set[0], self.cursor))
        return result[0] if result else False
    
    
    # def __del__(self):
    #     self.cursor.close()
    #     self.connector.close()
