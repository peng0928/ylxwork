# -*- coding: utf-8 -*-
# @Date    : 2022-08-24
# @Author  : chenxuepeng
import pymysql, re, datetime


class mysqlcheck:
    def __init__(self):
        self.host = '172.17.199.146'
        self.port = 3306
        self.user = 'green_finance'
        self.password = 'green_finance'
        self.db = 'doc'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    def select_all(self):
        table = 'buy_value_green_finance'
        sql = 'select id,buy_value from %s where attribute_id=6' %table
        self.cursor.execute(sql)
        select_result = self.cursor.fetchall()
        for item in select_result:
            id = item[0]
            date = self.timechange(item[1])
            self.cursor.execute('update buy_value_green_finance set buy_value="%s" where id=%s'%(date, id))
            self.conn.commit()

    def timechange(self, start_date):
        middle = datetime.datetime.strptime(start_date.replace('/', '-'), '%Y-%m-%d')
        end_date = datetime.datetime.strftime(middle, '%Y-%m-%d')
        return end_date

    def update(self):
        table = 'bidding_day_data_snapshots'
        up_list = ''
        for pid in up_list:
            sql = 'update %s set publishdate="" where id = "%s"'%(table, pid)
            self.cursor.execute(sql)
            print(pid, 'success')
            self.conn.commit()

    def update2(self):
        table = 'bidding_day_data_snapshots'
        up_list = []

        for pid in up_list:
            s_sql = 'SELECT publishdate FROM bidding_day_data_snapshots WHERE id="%s"'%(pid)
            self.cursor.execute(s_sql)
            sone = self.cursor.fetchone()[0].replace('年', '-').replace('月', '-').replace('日', '')
            up_date = re.findall('\d{4}-\d{1,2}-\d{1,2}', sone)[0]


            sql = 'update %s set publishdate="%s" where id = "%s"'%(table, up_date, pid)
            self.cursor.execute(sql)
            print(pid, 'success')
            self.conn.commit()

if __name__ == '__main__':
    P = mysqlcheck()
    P.select_all()