import pymysql, copy
from redis_conn import redis_conn


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        # self.host = '10.0.3.109'
        # self.port = 3356
        self.host = 'localhost'
        self.port = 3308
        self.user = 'root'
        # self.password = 'Windows!@#'
        # self.db = 'ubk_plugin'
        self.password = '123456'
        self.db = 'doc'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

        # redis去重名
        self.redis_field = 'risk_day_data_snapshots_nafmii:'
        # redis去重库位置
        self.redis_db = 8

    def insert_into_doc(self, fields=None):
        bank_name = fields['bank_name']
        pageurl = fields['pageurl']
        pub_date = fields['pub_date']
        bank_abbreviation = fields['bank_abbreviation']
        cause = fields['cause']
        decision = fields['decision']
        uuid = fields['uuid']

        sql = 'insert into risk_day_data_snapshots_nafmii (pageurl, pub_date, bank_name, bank_abbreviation, cause, decision) value ' \
              '("%s","%s","%s","%s","%s","%s")' % (pageurl, pub_date, bank_name, bank_abbreviation, cause, decision)
        try:
            select_result = self.conn_redis.find_data(field=self.redis_field, value=uuid)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入数据库{insert_id}:', bank_name, pageurl)
                self.conn.commit()

                ###################################################
                conn_redis = redis_conn(db=self.redis_db)
                conn_redis.set_add(field=self.redis_field, value=str(uuid))
                print('redis:', pageurl)
                ###################################################
            else:
                print('已存在:', sql)

        except Exception as e:
            print(e, sql)

    def close(self):
        self.cursor.close()
        self.conn.close()


class pymsysql_109(object):
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

    def bank_orgnike(self):
        orgnike = []
        sql = 'SELECT DISTINCT orgnike FROM risk_organizationtype_data'
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        for i in result:
            orgnike.append(i[0])
        return orgnike

    def __del__(self):
        self.cursor.close()
        self.conn.close()
