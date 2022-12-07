import pymysql, copy, re
from landchina.redis_conn import redis_conn
from landchina.data_process import *


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def insert_into_doc(self, fields=None, uuid=None):
        timestamp = microsecond_timestamp()
        select_result = self.conn_redis.find_data(value=uuid)
        if select_result is False:
            print(f'正在插入mysql数据库:', timestamp)

            for k, v in fields.items():
                sql = 'insert into buy_estate_market (attribute_id,buy_value,data_id) ' \
                      'values ("%s","%s","%s")' % (k, v, timestamp)
                try:
                    self.cursor.execute(sql)
                    self.conn.commit()
                except Exception as e:
                    print(e, sql)
            print(f'完成插入mysql数据库:', timestamp)
            ###################################################
            conn_redis = redis_conn(db=8)
            conn_redis.set_add('buy_estate_market', value=uuid)
            self.cursor.close()
            self.conn.close()
            print('正在插入redis数据库:', uuid)
        else:
            print('已存在:', )



    def select_value(self):
        sql = '''select id,gsdate from buy_estate_market'''
        self.cursor.execute(sql)
        fetchall = self.cursor.fetchall()
        for all in fetchall:
            id = all[0]
            gsdate = all[1]

            gsdate = gsdate.split('≤')[-1]
            usql = 'update buy_estate_market set gsdate="%s" where id=%s' % (gsdate, id)
            self.cursor.execute(usql)
            self.conn.commit()
            print(id, usql)

    def update_value(self):
        sql = '''select id,mj,crbzj,qsj,jjfd,cjjg,tzqd from buy_estate_market'''
        self.cursor.execute(sql)
        fetchall = self.cursor.fetchall()
        for all in fetchall:
            id = all[0]
            mj = all[1].replace('平方米', '')
            crbzj = all[2].replace('万元', '')
            qsj = all[3].replace('万元', '')
            jjfd = all[4].replace('万元', '')
            cjjg = all[5].replace('万元', '')
            tzqd = all[5].replace('万元/公顷', '')

            usql = 'update buy_estate_market set mj="%s",tzqd="%s", crbzj="%s", qsj="%s", jjfd="%s", cjjg="%s" ' \
                   ' where id=%s' % (mj, tzqd, crbzj, qsj, jjfd, cjjg, id)
            self.cursor.execute(usql)
            self.conn.commit()
            print(usql)

    def update_deal(self):
        sql = '''select id,jzmj,cjjg from buy_estate_market'''
        self.cursor.execute(sql)
        fetchall = self.cursor.fetchall()
        for all in fetchall:
            id = all[0]
            jzmj = all[1]
            cjjg = all[2]
            try:
                jzmj = float(jzmj)
                cjjg = float(cjjg)
                usql = 'update buy_estate_market set price="%.2f" where id=%s' % (cjjg/jzmj, id)
                self.cursor.execute(usql)
                self.conn.commit()
                print(usql)

            except:
                pass


if __name__ == '__main__':
    p = pymysql_connection().update_deal()
    print(p)
