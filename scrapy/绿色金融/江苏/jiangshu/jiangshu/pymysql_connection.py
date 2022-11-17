import pymysql, copy
from .redis_conn import redis_conn
from .data_process import *


class pymysql_connection():

    # mysql
    def __init__(self):
        self.host = '10.0.3.14'
        self.port = 3306
        self.user = 'root'
        self.password = '123456'
        self.db = 'doc'
        self.table = 'buy_value_green_finance'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):
        # print(fields)
        global data
        data_id = microsecond_timestamp()
        pageurl = fields['pageurl']

        # 地域的ID
        area_id = 11

        select_result = self.conn_redis.find_data(value=pageurl)
        if select_result is False:
            for i in range(1, 9):
                if i == 1:
                    data = fields['Penalty_doc_num']
                if i == 2:
                    data = fields['Company_name']
                if i == 3:
                    data = fields['Offences']
                if i == 4:
                    data = fields['Punishment_basis']
                if i == 5:
                    data = fields['Penalty_content']
                if i == 6:
                    data = fields['Penalty_date']
                if i == 7:
                    data = fields['penalty_unit']
                if i == 8:
                    data = fields['Penalty_amount']

                if data is None:
                    pass
                else:
                    if i == 5:
                        insert_snapshots = 'insert into green_finance_data_snapshots(content)value("%s")' % (data)
                        self.cursor.execute(insert_snapshots)
                        insert_id = self.conn.insert_id()
                        self.conn.commit()
                        print('正在插入snapshots:', data)

                        insert_sql = 'insert into buy_value_green_finance(area_id, attribute_id, buy_value, data_id)value(%d,%d,"%s",%d)' % (
                        area_id, i, insert_id, data_id)
                        self.cursor.execute(insert_sql)
                        self.conn.commit()
                        print('正在插入:', data, data_id)
                    else:
                        insert_sql = 'insert into buy_value_green_finance(area_id, attribute_id, buy_value, data_id)value(%d,%d,"%s",%d)' % (
                        area_id, i, data, data_id)
                        self.cursor.execute(insert_sql)
                        self.conn.commit()
                        print('正在插入:', data, data_id)

            self.conn_redis.set_add(value=pageurl)

        else:
            print('存在：', pageurl)