import sqlite3
import os
from dataclasses import dataclass
from datetime import datetime
from custom_exceptions import DatabaseException


@dataclass
class View:
    __ip: str
    __message_id: str

    def __init__(self, ip: str, id: int):
        self.set_ip(ip)
        self.set_message_id(id)

    def set_ip(self, ip: str):
        if len(str(ip).split('.')) != 4:
            raise DatabaseException(f"Invalid ip address {self.__ip}")
        self.__ip = ip

    def set_message_id(self, id: int):
        self.__message_id = str(id)

    def get_message_values(self):
        if self.__ip == None or self.__message_id == None:
            raise DatabaseException("View class has not been initialized yet.")
        return self.__ip, self.__message_id


@dataclass
class Message:
    __ip: str
    __message: str
    __date: str
    __id: int

    def __init__(self, ip: str, message: str, date_str=None, id=None):
        date = datetime.now()
        self.set_ip(ip)
        self.set_message(message)
        self.__id = id
        if date_str != None:
            self.__date = date_str
        else:
            self.set_date(date.year, date.month, date.day, date.hour, date.minute, date.second)

    def get_id(self):
        if self.__id:
            return self.__id
        return 0

    def set_date(self, year: int, month: int, day: int, hour: int, minute: int, second: int):
        add_zero = lambda x: x if len(str(x)) == 2 else f'0{x}'
        self.__date = f'{year}/{add_zero(month)}/{add_zero(day)}-{add_zero(hour)}:{add_zero(minute)}:{add_zero(second)}'

    def set_ip(self, ip: str):
        if len(str(ip).split('.')) != 4:
            raise DatabaseException(f"Invalid ip address {self.__ip}")
        self.__ip = ip

    def set_message(self, message: str):
        if len(message.strip()) == 0:
            raise DatabaseException(f"Blank Message {self.__message}")
        self.__message = message

    def get_message(self):
        return f'[{self.__ip} - {self.__date}] > [{self.__message}]'

    def get_message_values(self):
        if self.__ip == None or self.__message == None or self.__date == None:
            raise DatabaseException("Message class has not been initialized yet.")
        return self.__ip, self.__message, self.__date


class Database:
    def __init__(self):
        self.db_name =  'pardus_kuramayanlar.db'
        self.chat_table_name = 'Chat'
        self.view_table_name = 'View'

        initialize = not os.path.exists(self.db_name)
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()

        if initialize:
            self.cursor.execute(
                f'CREATE TABLE {self.chat_table_name}(id INTEGER PRIMARY KEY AUTOINCREMENT,ip TEXT,message TEXT,date TEXT);')
            self.cursor.execute(
                f'CREATE TABLE {self.view_table_name}(ip TEXT,message_id INTEGER,FOREIGN KEY(message_id) REFERENCES Chat(id));')
            self.connection.commit()

    def execute(self, sql: str):
        self.cursor.execute(sql)
        self.connection.commit()
        return self.cursor.lastrowid

    def fetch(self, sql):
        return list(self.cursor.execute(sql))

    def close(self):
        self.connection.commit()
        self.connection.close()


class DatabaseHandler:
    __database = None

    def __init__(self):
        self.__database = Database()

    def insert_view(self, v: View):
        sql_query = f'INSERT INTO {self.__database.view_table_name}(ip,message_id) VALUES{v.get_message_values()}'
        self.__database.execute(sql_query)

    def insert_message(self, m: Message):
        sql_query = f"INSERT INTO {self.__database.chat_table_name}(ip,message,date) VALUES{m.get_message_values()}"
        id = self.__database.execute(sql_query)
        return id

    def get_messages(self, ip: str):
        messages = []
        sql_query = 'SELECT message_id FROM ' + self.__database.view_table_name + f' WHERE ip="{ip}"'
        message_ids = self.__database.fetch(sql_query)
        message_ids = [m[0] for m in message_ids]
        message_ids.sort()
        sql_query = 'SELECT * FROM ' + self.__database.chat_table_name + f' WHERE id > {0 if len(message_ids) == 0 else message_ids[-1]}'
        messages_sql = self.__database.fetch(sql_query)
        for message in messages_sql:
            msg_id = message[0]
            if msg_id not in message_ids:
                m = Message(message[1], message[2], message[3], id=msg_id)
                messages.append(m)

        return messages

