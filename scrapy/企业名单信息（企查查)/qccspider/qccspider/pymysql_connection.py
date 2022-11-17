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

    def qcc_insert(self, key, value, sonlist, fathlist):
        # try:
            qccdata_table = 'buy_business_qccdata'
            qcc_business_table = 'buy_business_qccshareholdes'
            data_insert_sql = 'insert into %s (%s) values (%s)' % (qccdata_table, key, value)
            self.cursor.execute(data_insert_sql)
            insert_id = self.conn.insert_id()
            self.conn.commit()
            print('工商数据存储成功:', insert_id)

            "股权穿透图-子级"
            for i in sonlist:
                son_k = []
                son_v = []
                for k, v in i.items():
                    son_k.append(k)
                    son_v.append(v)
                sql_k = ','.join(son_k)
                son_v = ['"' + str(i) + '"' for i in son_v]
                sql_v = ','.join(son_v)

                sql_k += ',pid'
                sql_v += ',"%s"' % insert_id
                print(sql_k)
                print(sql_v)
                son_insert_sql = 'insert into %s (%s) values (%s)' % (qcc_business_table, sql_k, sql_v)
                self.cursor.execute(son_insert_sql)
                insert_id = self.conn.insert_id()
                self.conn.commit()
            print('股权穿透图-子级 存储成功:', insert_id)

            "股权穿透图-父级"
            for i in fathlist:
                fath_k = []
                fath_v = []
                for k, v in i.items():
                    fath_k.append(k)
                    fath_v.append(v)
                fath_k = ','.join(fath_k)
                fath_v = ['"' + str(i) + '"' for i in fath_v]
                fath_v = ','.join(fath_v)

                fath_k += ',pid'
                fath_v += ',"%s"' % insert_id
                son_insert_sql = 'insert into %s (%s) values (%s)' % (qcc_business_table, fath_k, fath_v)
                self.cursor.execute(son_insert_sql)
                insert_id = self.conn.insert_id()
                self.conn.commit()

            print('股权穿透图-父级 存储成功:', insert_id)

        # except Exception as e:
        #     print(e)



    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    p = pymysql_connection()
    # p.get_purchasing_name()
