# -*- coding: utf-8 -*-
# @Date    : 2023-01-02 16:34
# @Author  : chenxuepeng
import csv, pymysql




class mysql_conn():
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    def mysqlconn(self):
        with open('test.csv', mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
        sql = "SELECT * FROM buy_business_qccdata WHERE type=3 and `level` = 0 and area like ('%广西%')"
        self.cursor.execute(sql)
        all = self.cursor.fetchall()
        for item in all:
            flist = []
            print(list(item))
            writer.writerow(list(item))
            id = item[0]
            end = item[2]
            print(type(end), end)
            if end == 0:
                pass

    def rel(self):
        selectsql = 'select id,pid from buy_business_qccdata where level != 1 and level != 2'
        self.cursor.execute(selectsql)
        getall = self.cursor.fetchall()
        for query in getall:
            cid = query[0]
            pid = query[1]
            sql = 'insert into buy_business_qccdata_rel (cid, pid) values ("%s", "%s")' % (cid, pid)
            self.cursor.execute(sql)
            self.conn.commit()
            print(cid, pid)


if __name__ == '__main__':
    p = mysql_conn()
    p.rel()