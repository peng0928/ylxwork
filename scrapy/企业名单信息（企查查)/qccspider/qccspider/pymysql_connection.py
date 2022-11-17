import pymysql


class pymysql_connection():
    """企查查"""
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
        # self.conn_redis = redis_conn()

    def qcc_insert(self, key, value):
        qccdata_table = 'buy_business_qccdata'
        qcc_business_table = 'buy_business_qccshareholdes'
        data_insert_sql = 'insert into %s (%s) values (%s)' % (qccdata_table, key, value)
        self.cursor.execute(data_insert_sql)
        insert_id = self.conn.insert_id()
        print(data_insert_sql, insert_id)
        self.conn.commit()





    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    p = pymysql_connection()
    # p.get_purchasing_name()
