import pymysql, copy
from .redis_conn import redis_conn


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        # self.db = 'doc'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):

        companyCd = fields['companyCd']
        companyName = fields['companyName']
        destFilePath = fields['destFilePath']
        publishDate = fields['publishDate']
        disclosureTitle = fields['disclosureTitle']
        fileName = fields['fileName']
        status = fields['status']
        stockName = fields['stockName']

        if redis_value is None:
            redis_value = destFilePath
        else:
            redis_value = redis_value

        sql = 'insert into listed_company_pdf (companyCd, companyName, destFilePath, publishDate,' \
              ' disclosureTitle, fileName, status, stockName) value ' \
              '("%s","%s","%s","%s","%s", "%s", "%s", "%s")' % (companyCd, companyName, destFilePath, publishDate,
                                                                disclosureTitle, fileName, status, stockName)
        try:
            redis_select_values = destFilePath

            select_result = self.conn_redis.find_data(value=redis_select_values)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入数据库{insert_id}:', companyCd, companyName)
                self.conn.commit()

                ###################################################
                conn_redis = redis_conn(db=8)
                conn_redis.set_add('证券交易所:', value=destFilePath)
                print('redis:', destFilePath)
                ###################################################


                # reids断点
                if redis_field != None:
                    self.conn_redis.del_data(field=redis_field, value=redis_value)

            else:
                print('已存在:', sql)
                if redis_field != None:
                    self.conn_redis.del_data(field=redis_field, value=redis_value)

        except Exception as e:
            print(e, sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
