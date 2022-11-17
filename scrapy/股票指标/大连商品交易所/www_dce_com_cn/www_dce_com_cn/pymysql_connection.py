import pymysql, copy
from .redis_conn import redis_conn
from .data_process import *


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.table = 'buy_value_futures'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):
        # print(fields)
        global data
        data_id = microsecond_timestamp()
        redis_key = fields['pageurl'] + fields['CONTRACT_CODE']  # 去重配置： 链接+合约代码
        redis_key = encrypt_md5(redis_key)
        # 地域的ID
        company_id = 2

        select_result = self.conn_redis.find_data(value=redis_key)
        if select_result is False:
            for i in range(1, 17):
                if i == 1:
                    data = fields['DATE']
                if i == 2:
                    data = fields['EXCHANGE_PLACE']
                if i == 3:
                    data = fields['PRODUCTNAME']
                if i == 4:
                    data = fields['CONTRACT_CODE']
                if i == 5:
                    data = fields['OPENPRICE']
                if i == 6:
                    data = fields['HIGHESTPRICE']
                if i == 7:
                    data = fields['LOWESTPRICE']
                if i == 8:
                    data = fields['CLOSEPRICE']
                if i == 9:
                    data = fields['SETTLEMENTPRICE']
                if i == 10:
                    data = fields['PRESETTLEMENTPRICE']
                if i == 11:
                    data = fields['ZD1_CHG']
                if i == 12:
                    data = fields['ZD2_CHG']
                if i == 13:
                    data = fields['VOLUME']
                if i == 14:
                    data = fields['OPENINTEREST']
                if i == 15:
                    data = fields['OPENINTERESTCHG']
                if i == 16:
                    data = fields['TURNOVER']

                if data is None:
                    pass
                else:
                        insert_sql = 'insert into buy_value_futures(company_id, attribute_id, buy_value, data_id)value(%d,%d,"%s",%d)' % (
                        company_id, i, data, data_id)
                        self.cursor.execute(insert_sql)
                        self.conn.commit()
                        print('正在插入:', insert_sql)
            self.conn_redis.set_add(value=redis_key)

        else:
            print('存在：', redis_key)