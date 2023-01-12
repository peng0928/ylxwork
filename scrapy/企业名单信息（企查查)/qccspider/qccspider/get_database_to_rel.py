from decorator_penr import *
from qcc_hmac import *
from useragent import *
from qcc_database_mysql import *
from redis_conn import *
from data_process import *
from config import *


class QccMySql:
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.redisConn = redis_conn()

    def MainRun(self):
        investmentTable = 'buy_business_qcc_investment_new'
        qccDataTable = 'buy_business_qccdata_new'
        qccRelTable = 'buy_business_qccdata_rel_new'
        invSqlCount = 'select distinct cid from %s' % investmentTable
        relSql = 'select distinct cid from %s' % investmentTable
        invRes = self.SelectForSQL(invSql)
        print(invRes)
        for query in invRes:
            cid = query[0]

    def SelectForSQL(self, sql):
        self.cursor.execute(sql)
        allData = self.cursor.fetchall()
        return allData


if __name__ == '__main__':
    Penr = QccMySql()
    Penr.MainRun()
