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

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):
        uuid = fields['uuid']
        del fields['uuid']
        klist = []
        vlist = []
        for k, v in fields.items():
            klist.append(k)
            vlist.append(v)

        av = ['"' + str(i) + '"' for i in vlist]
        k = ','.join(klist)
        v = ','.join(av)

        number = fields['number']  # '宗地编号',
        # xzq = fields['xzq']  # '行政区(内容页)',
        # zdzl = fields['zdzl']  # '土地坐落',
        # tdyt = fields['tdyt']  # '土地用途',
        # crcx = fields['crcx']  # '出让年限',
        # mj = fields['mj']  # '出让面积',
        # rjl = fields['rjl']  # '容积率',
        # jzmd = fields['jzmd']  # '建筑密度',
        # gyfs = fields['gyfs']  # '供应方式',
        # tdjb = fields['tdjb']  # '土地级别',
        # jzmj = fields['jzmj']  # '建筑面积',
        # lhl = fields['lhl']  # '绿化率',
        # jzxg = fields['jzxg']  # '建筑限高',
        # bmjz = fields['bmjz']  # '报名截止时间',
        # bmqs = fields['bmqs']  # '报名起始时间',
        # zpjz = fields['zpjz']  # '招拍挂截止时间',
        # zpqs = fields['zpqs']  # '招拍挂起始时间',
        # crbzj = fields['crbzj']  # '竞买保证金',
        # qsj = fields['qsj']  # '起始价',
        # jjfd = fields['jjfd']  # '加价幅度',
        # cjjg = fields['cjjg']  # '成交价',
        # gsdate = fields['gsdate']  # '成交公示日期',
        # tzqd = fields['tzqd']  # '投资强度',
        # srdw = fields['srdw']  # '受让人',
        # pubdate = fields['fbsj']  # '发布时间',

        sql = 'insert into buy_estate_market (%s) values (%s)' % (k, v)
        try:
            select_result = self.conn_redis.find_data(value=uuid)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入mysql数据库:', insert_id, number)
                self.conn.commit()
                ###################################################
                conn_redis = redis_conn(db=8)
                conn_redis.set_add('buy_estate_market', value=uuid)
                print('正在插入redis数据库:', uuid)
                ###################################################
            else:
                print('已存在:', number)

        except Exception as e:
            print(e, sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()

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
