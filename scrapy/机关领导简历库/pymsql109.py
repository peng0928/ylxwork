# -*- coding: utf-8 -*-
# @Date    : 2022-10-09 15:53
# @Author  : chenxuepeng
import pymysql, copy
from pymysql.converters import escape_string


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    def get_leader(self):
        self.cursor.execute('select id, provincial, prefecture, type, position, leader_name from org_leader')
        fetchall = self.cursor.fetchall()
        self.cursor.close()
        return fetchall

    def update_leader(self, record, parse_result, id, native_place, education, birthday):
        if record == 'null':
            sql = 'update org_leader set record=%s, parse_result="%s", birthday="%s" where id="%s"' % (record, parse_result, birthday, id)
        else:
            sql = 'update org_leader set record="%s", parse_result="%s", native_place="%s", education="%s", birthday="%s" where id="%s"' % (
            record, parse_result, native_place, education, birthday, id)
            if education is None:
                sql = sql.replace('education="None"', 'education=null')
            if native_place is None:
                sql = sql.replace('native_place="None"', 'native_place=null')
        if birthday is None:
            sql = sql.replace('birthday="None"', 'birthday=null')
        self.cursor.execute(sql)
        self.conn.commit()
        print('update:', id)
        self.cursor.close()
        self.conn.close()
