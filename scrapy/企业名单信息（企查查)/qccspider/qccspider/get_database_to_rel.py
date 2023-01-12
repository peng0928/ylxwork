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
        self.redisMain = 'qccMainCompany'
        self.investmentTable = 'buy_business_qcc_investment_new'
        self.qccDataTable = 'buy_business_qccdata_new'
        self.qccRelTable = 'buy_business_qccdata_rel_new'
        self.qccOriTable = 'buy_business_qcc_enterprisetype_qccdata'

    def MainRun(self):
        """在对外投资数据库中找出关系缺少并修复"""
        invSql = 'select cid,count(*) as count from %s group by cid;' % self.investmentTable
        relSql = 'select pid,count(*) as count from %s group by pid' % self.qccRelTable
        relRes = self.SelectForSQL(relSql)
        relDict = {}
        for query in relRes:
            relDict[query[0]] = query[1]
        invRes = self.SelectForSQL(invSql)
        for query in invRes:
            id = query[0]
            count = query[1]
            msg = '*****************公司id:' + str(id) + ' 对外投资数:' + str(count)
            print(msg)
            relGet = relDict.get(id)
            if relGet:
                if count != relGet:
                    print(f'对外投资数不匹配:{id}, 对外投资:{count}, 关系数: {relGet}')
                    # self.BigCase(id)
                    # investData = self.BigInvest(id)
                else:
                    print('数据一致性:', id)
            else:
                print('未找到:', id)
                investData = self.BigInvest(id)
                invType, invLevel = self.SelectWhere(whereKeys=['id'], whereValues=[
                    id], table=self.qccDataTable, selectKey='type,level')
                for query in investData:
                    getPdata = self.SelectWhere(whereKeys=['name'], whereValues=[
                                                query], table=self.qccDataTable)
                    print(query, bool(getPdata))
                    if bool(getPdata):
                        getSonID = getPdata[0]
                        print('------yes:', query)
                        self.InsertRel(getSonID, id)
                    else:
                        print('------no:', query)
                        key = 'pid, level, name, type'
                        level = int(invLevel) - 1
                        value = f'"{id}","{level}", "{query}", "{invType}" '
                        self.NotFInsertRel(
                            key=key, value=value, id=id, oritype=invType, name=query)

    def SelectForSQL(self, sql, fetchone=False):
        self.cursor.execute(sql)
        if fetchone:
            allData = self.cursor.fetchone()
        else:
            allData = self.cursor.fetchall()
        return allData

    def BigCase(self, id):
        RelNameList = []
        SelRelCidSql = 'select cid from %s where pid=%s' % (
            self.qccRelTable, id)
        RelResult = self.SelectForSQL(SelRelCidSql)
        for query in RelResult:
            RelID = query[0]
            SelRelName = 'select name from %s where id = %s' % (
                self.qccDataTable, RelID)
            RelNameResult = self.SelectForSQL(SelRelName, fetchone=True)
            RelNameResult = RelNameResult[0]
            print(RelNameResult)

    def BigInvest(self, id):
        """找出对外投资数据库所有公司名称"""
        InvNameList = []
        SelRelCidSql = 'select StockName from %s where cid=%s' % (
            self.investmentTable, id)
        RelResult = self.SelectForSQL(SelRelCidSql)
        for query in RelResult:
            InvNameResult = query[0]
            InvNameList.append(InvNameResult)
        return InvNameList

    def SelectWhere(self, table, whereKeys, whereValues, selectKey=None, fetchone=True):
        selectKey = selectKey if selectKey else '*'
        whereStr = [whereKeys[i] + '=' + '"%s"' % whereValues[i]
                    for i in range(len(whereKeys))]
        whereStr = ''.join(whereStr)
        sql = 'select %s from %s where %s' % (selectKey, table, whereStr)
        self.cursor.execute(sql)
        if fetchone:
            return self.cursor.fetchone()
        else:
            return self.cursor.fetchall()

    def InsertRel(self, cid, pid):
        """插入下级关系"""
        try:
            sql = 'insert into %s (cid, pid) values ("%s", "%s")' % (
                self.qccRelTable, cid, pid)
            self.cursor.execute(sql)
            self.conn.commit()
            print('下级关系插入成功:', cid, pid)
        except:
            print('该关系已存在:', cid, pid)

    def NotFInsertRel(self, key, value, id, oritype, name):
        """对不存在的公司进行插入"""
        try:
            sql = 'insert into %s (%s) values (%s)' % (
                self.qccDataTable, key, value)
            self.cursor.execute(sql)
            InsertID = self.conn.insert_id()
            self.conn.commit()
            self.cursor.execute('insert into %s (enterprisetypeid, dataid) value ("%s", "%s")' %
                                (self.qccOriTable, oritype, InsertID))
            self.conn.commit
            self.InsertRel(InsertID, id)
            redis_conn().set_add(field=self.redisMain, value=name)
            print('0补充成功:', id, InsertID)
        except:
            self.conn.rollback()
            print('0补充失败:', id)


if __name__ == '__main__':
    Penr = QccMySql()
    Penr.MainRun()
