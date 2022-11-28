import pymysql, uuid
from redis_conn import redis_conn


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
        self.conn_redis = redis_conn()

    def qcc_insert(self, key, value, shareholder=None, investment=None, uuid=None):
        global  shareholder_id, investment_id
        try:
            qccdata_table1 = 'buy_business_qccdata'  # 企业名单信息
            qccdata_table2 = 'buy_business_qcc_investment'  # 对外投资
            qccdata_table3 = 'buy_business_qcc_shareholderinformation'  # 股东信息
            qcc_business_table = 'buy_business_qccshareholdes'
            if key and value:
                data_insert_sql = 'insert into %s (%s) values (%s)' % (qccdata_table1, key, value)
                self.cursor.execute(data_insert_sql)
                insert_id = self.conn.insert_id()
                data_insert_sql2 = 'UPDATE %s set pid="%s", end="0", code="%s" where id=%s' % (
                    qccdata_table1, insert_id, insert_id, insert_id)
                self.cursor.execute(data_insert_sql2)
                self.conn.commit()
                print('工商数据存储成功:', insert_id)
            else:
                print('工商数据存储失败:', )
                insert_id = None

            if insert_id:
                "股东信息"
                if shareholder:
                    print('\033[1;32m正在插入父公司:\033[0m')
                    for l in shareholder:
                        str_k = ''
                        str_v = ''
                        """父公司"""
                        StockName = l.get('StockName')
                        key1 = 'name, pid, end, level'
                        value1 = f'"{StockName}"' + f',"{insert_id}","{1}","{2}"'
                        shareholder_sql = 'insert into %s (%s) values (%s)' % (qccdata_table1, key1, value1)
                        self.cursor.execute(shareholder_sql)
                        shareholder_id = self.conn.insert_id()
                        shareholder_sql2 = 'update %s set code="%s" where id=%s' % (
                            qccdata_table1, str(insert_id) + '.' + str(shareholder_id), shareholder_id)
                        self.cursor.execute(shareholder_sql2)
                        self.conn.commit()

                        for k, v in l.items():
                            str_k += f"{k}" + ','
                            str_v += f'"{v}"' + ','
                        str_k += 'id'
                        str_v += f'{shareholder_id}'
                        shareholder_sql3 = 'insert into %s (%s) values (%s)' % (qccdata_table3, str_k, str_v)
                        self.cursor.execute(shareholder_sql3)
                        self.conn.commit()
                    print('完成插入父公司股东信息')

                "对外投资"
                if investment:
                    print('\033[1;32m正在插入子公司: \033[0m')
                    for l in investment:
                        str_k = ''
                        str_v = ''
                        StockName = l.get('StockName')
                        """子公司"""
                        key1 = 'name, pid, end, level'
                        value1 = f'"{StockName}"' + f',"{insert_id}","{1}","{0}"'
                        shareholder_sql = 'insert into %s (%s) values (%s)' % (qccdata_table1, key1, value1)
                        self.cursor.execute(shareholder_sql)
                        investment_id = self.conn.insert_id()
                        investment_sql2 = 'update %s set code="%s" where id=%s' % (
                            qccdata_table1, str(insert_id) + '.' + str(investment_id), investment_id)
                        self.cursor.execute(investment_sql2)
                        self.conn.commit()

                        for k, v in l.items():
                            str_k += f"{k}" + ','
                            str_v += f'"{v}"' + ','
                        str_k += 'id'
                        str_v += f'{investment_id}'
                        investment_sql3 = 'insert into %s (%s) values (%s)' % (qccdata_table2, str_k, str_v)
                        self.cursor.execute(investment_sql3)
                        self.conn.commit()
                    print('完成插入')

                self.conn_redis.set_add(value=uuid)
                print('reids 存储成功:')


        except Exception as e:
            print(e)


    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    p = pymysql_connection()
    # p.get_purchasing_name()
