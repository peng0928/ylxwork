import pymysql, copy
from .redis_conn import redis_conn


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
        xzqFullName = fields['xzqFullName']
        zdh = fields['zdh']
        zdZl = fields['zdZl']
        mj = str(fields['mj'])
        tdYt = fields['tdYt']
        gyFs = fields['gyFs']
        fbSj = fields['fbSj']
        uuid = fields['uuid']
        sql = 'insert into buy_estate_market (district, number, location, total_area, land, supply, pubdate) values ("%s","%s","%s","%s","%s","%s","%s")' % (xzqFullName, zdh, zdZl, mj, tdYt, gyFs, fbSj)
        try:
            select_result = self.conn_redis.find_data(value=uuid)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入mysql数据库:', insert_id, xzqFullName, zdZl, fbSj)
                self.conn.commit()
                ###################################################
                conn_redis = redis_conn(db=8)
                conn_redis.set_add('buy_estate_market', value=uuid)
                print('正在插入redis数据库:', uuid)
                ###################################################
            else:
                print('已存在:', (xzqFullName, zdh, zdZl, mj, tdYt, gyFs, fbSj))

        except Exception as e:
            print(e, sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
