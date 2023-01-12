import pymysql
import uuid
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
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def qccUpdate(self, litem, ids=None, shareholder=None, investment=None, Type=None, searchName=None):
        insert_id = ids
        try:
            mainTable = 'buy_business_qccdata_new'  # 企业名单信息
            investmentTable = 'buy_business_qcc_investment_new'  # 对外投资
            shareholderTable = 'buy_business_qcc_shareholderinformation_new'  # 股东信息
            if litem:
                data_insert_sql2 = 'UPDATE %s set %s where id=%s' % (
                    mainTable, litem, ids)
                self.cursor.execute(data_insert_sql2)
                self.conn.commit()
                print('工商数据 更新成功:', ids)

            else:
                print('工商数据存储失败:', )

            "股东信息"
            if shareholder:
                redsi_name = str(insert_id) + '_' + searchName
                print('\033[1;32m正在插入股东信息:\033[0m')
                self.insert_shareholderinformation_new(
                    item=shareholder, insert_id=insert_id, redsi_name=redsi_name)
            else:
                print('股东信息 不存在')

            "对外投资"
            if investment:
                print('\033[1;32m正在插入对外投资: \033[0m')
                redsi_name = str(insert_id) + '_' + searchName
                tablename = 'buy_business_qcc_investment_new'
                findbool = redis_conn().find_data(field=tablename, value=redsi_name)
                if findbool:
                    print('对外投资信息已存在:', redsi_name)
                else:
                    self.insert_qcc_investment_new(
                        item=investment, insert_id=insert_id, redsi_name=redsi_name)
                    for l in investment:
                        StockName = l.get('StockName')
                        """子公司"""
                        key1 = 'name, pid,  type'
                        value1 = f'"{StockName}"' + f',"{insert_id}", "{Type}"'
                        shareholder_sql = 'insert into %s (%s) values (%s)' % (
                            qccdata_table1, key1, value1)
                        self.cursor.execute(shareholder_sql)
                        shareholderid = self.conn.insert_id()
                        self.conn.commit()
                        """插入关系"""
                        self.cursor.execute('insert into buy_business_qccdata_rel (cid, pid) values ("%s", "%s")' % (
                            shareholderid, insert_id))
                        self.conn.commit()
                    print('完成插入')
            else:
                print('对外投资 不存在')

        except Exception as e:
            print(e)

    def insert_shareholderinformation_new(self, item, insert_id, redsi_name):
        redisConn = redis_conn()
        field = 'qcc_shareholderinformation_new'
        tablename = 'buy_business_qcc_shareholderinformation_new'
        findbool = redisConn.find_data(field=field, value=redsi_name)
        if findbool:
            print('股东信息已存在:', redsi_name)
        else:
            for l in item:
                str_k = ''
                str_v = ''
                for k, v in l.items():
                    str_k += f"{k}" + ','
                    str_v += f'"{v}"' + ','
                str_k += 'cid'
                str_v += f'{insert_id}'
                investment_sql3 = 'insert into %s (%s) values (%s)' % (
                    tablename, str_k, str_v)
                self.cursor.execute(investment_sql3)
                self.conn.commit()
            redisConn.set_add(field=field, value=redsi_name)
            print('股东信息Redis插入成功:', redsi_name)

    def insert_qcc_investment_new(self, item, insert_id, redsi_name):
        redisConn = redis_conn()
        tablename = 'buy_business_qcc_investment_new'
        findbool = redisConn.find_data(field=tablename, value=redsi_name)
        if findbool:
            print('对外投资信息已存在:', redsi_name)
        else:
            for l in item:
                str_k = ''
                str_v = ''
                for k, v in l.items():
                    str_k += f"{k}" + ','
                    str_v += f'"{v}"' + ','
                str_k += 'cid'
                str_v += f'{insert_id}'
                investment_sql3 = 'insert into %s (%s) values (%s)' % (
                    tablename, str_k, str_v)
                self.cursor.execute(investment_sql3)
                self.conn.commit()
            redisConn.set_add(field='qcc_investment_new', value=redsi_name)
            print('对外投资Redis插入成功:', redsi_name)

    def test(self):
        sql = 'select * from buy_business_qccdata where type = 0'
        self.cursor.execute(sql)
        getres = self.cursor.fetchall()
        for item in getres:
            ids = item[0]
            isql = 'insert into buy_business_qcc_enterprisetype_qccdata (enterprisetypeid,dataid) values ("%s","%s")' % (
                1, ids)
            self.cursor.execute(isql)
            self.conn.commit()
            print('success')

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    p = pymysql_connection().t01()
    # p.get_purchasing_name()
