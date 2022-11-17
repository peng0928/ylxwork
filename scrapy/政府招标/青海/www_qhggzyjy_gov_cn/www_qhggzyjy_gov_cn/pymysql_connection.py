import pymysql, copy
from ccgp_shandong_gov_cn.redis_conn import redis_conn


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.3.14'
        self.port = 3306
        self.user = 'root'
        self.password = '123456'
        self.db = 'doc'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def insert_into_doc(self, fields=None, tablename=None, str1='', str2='',
                        redis_field=None, redis_value=None):
        contenttype = fields['contenttype']
        pageurl = fields['pageurl']
        if redis_value is None:
            redis_value = pageurl
        else:
            redis_value = redis_value
        dict = copy.deepcopy(fields)
        del dict['doc_content']
        for k, v in dict.items():
            str1 += k + ','
            if v is not None:
                str2 += f'"{v}"' + ','
        key = str1[:-1]
        value = str2[:-1]
        sql = f'insert into {tablename} ({key}) value ({value})'

        try:
            select_sql = f'select * from {tablename} where ({key}) = ({value})'
            self.cursor.execute(select_sql)
            select_result = self.cursor.fetchone()
            if not select_result:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入数据库{insert_id}:', value)
                self.conn.commit()

                if contenttype == 0:
                    sql_insert_into_page = f'''insert into bidding_day_data_snapshots_page (id,content)value({insert_id},'{fields['doc_content']}')'''
                    print(f'正在插入数据库page:', insert_id)
                    self.cursor.execute(sql_insert_into_page)
                    self.conn.commit()

                    # reids断点
                    if redis_field != None:
                        self.conn_redis.del_data(field=redis_field, value=redis_value)
            else:
                print('---------已存在-------', sql)
                if redis_field != None:
                    self.conn_redis.del_data(field=redis_field, value=redis_value)

        except Exception as e:
            print(e, sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
