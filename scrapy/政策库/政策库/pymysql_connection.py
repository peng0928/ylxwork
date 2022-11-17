import pymysql, copy
from redis_conn import redis_conn


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.2.248'
        self.port = 3306
        self.user = 'penr'
        self.password = '521014'
        self.db = 'doc'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()
        self.redis_field = 'risk_day_data_snapshots_nafmii:'

    def insert_into_doc(self, fields=None):
        bank_name = fields['bank_name']
        pageurl = fields['pageurl']
        docsubtitle = fields['docsubtitle']
        pub_date = fields['pub_date']
        bank_abbreviation = fields['bank_abbreviation']
        cause = fields['cause']
        decision = fields['decision']
        uuid = fields['uuid']

        sql = 'insert into policy_day_data_snapshots (pageurl, pub_date, bank_name, bank_abbreviation, cause, decision) value ' \
              '("%s","%s","%s","%s","%s","%s")' % (pageurl, pub_date, bank_name, bank_abbreviation, cause, decision)
        try:
            select_result = self.conn_redis.find_data(field=self.redis_field, value=uuid)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入数据库{insert_id}:', docsubtitle, pageurl)
                self.conn.commit()

                ###################################################
                conn_redis = redis_conn(db=8)
                conn_redis.set_add(field=self.redis_field, value=str(uuid))
                print('redis:', pageurl)
                ###################################################
            else:
                print('已存在:', sql)

        except Exception as e:
            print(e, sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
