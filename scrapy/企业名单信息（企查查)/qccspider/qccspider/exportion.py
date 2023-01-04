# -*- coding: utf-8 -*-
# @Date    : 2023-01-02 16:34
# @Author  : chenxuepeng
import csv, pymysql


class mysql_conn():
    def __init__(self):
        self.host = '10.0.3.109'
        self.port = 3356
        self.user = 'root'
        self.password = 'Windows!@#'
        self.db = 'ubk_plugin'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    def mysqlconn(self):
        with open('test.csv', mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
        sql = "SELECT * FROM buy_business_qccdata WHERE type=3 and `level` = 0 and area like ('%广西%')"
        self.cursor.execute(sql)
        all = self.cursor.fetchall()
        for item in all:
            flist = []
            print(list(item))
            writer.writerow(list(item))
            id = item[0]
            end = item[2]
            print(type(end), end)
            if end == 0:
                pass

    def export_gx(self):
        self.key01 = [
            # 'pageurl','label','统一社会信用代码','企业名称','法定代表人','登记状态','状态','成立日期','注册资本','实缴资本',
            'pageurl','label','credit_code','name','legal_representative','registration_status','status','incorporation_date','registered_capital','paid_capital',

            'organization_code', 'business_code', 'taxpayer_code', 'enterprise_type', 'business_term', 'taxpayer_qualification', 'personnel_size', 'insured_num', 'approval_date', 'area', 'organ',

            'io_code', 'industry', 'english_name', 'address', 'business_scope', 'report_latest',
        ]
        self.key02 = [
            'name', 'Status', 'FundedRatio', 'ShouldCapi',
            'ShouldDate', 'ProvinceName', 'Industry', 'ProductName', 'Industry',
        ]
        sql = 'select id from buy_business_qccdata where level=1 and end=0 and area like ("%广西%")'
        self.cursor.execute(sql)
        getdata = self.cursor.fetchall()
        for query in getdata[0:1]:
            # nid = query[0]
            nid = '40922'
            sdata = self.select_data(nid)
            fdata = self.select_father(nid)
            if fdata:
                sdata.update({
                        'upward': {
                            "direction": "upward",
                            "name": "origin",
                            "children": [fdata]

                        }
                     })

            """子公司"""
            list2 = []
            for query2 in self.select_son(nid=nid):
                cid = query2[0]
                nid2 = query2[1]
                data2 = self.select_investment(cid)
                print('子公司:', data2)

                """孙公司"""

                data3 = self.select_son(nid=cid)
                if data3:
                    sgs_list = []
                    for query3 in data3:
                        sgs = self.select_investment(query3[0])
                        sgs_list.append(sgs)
                        print('孙公司:', sgs)
                    data2.update({
                        "children": sgs_list
                    })
                    list2.append(data2)
                else:
                    list2.append(data2)

            if list2:
                sdata.update({
                        'downward': {
                            "direction": "downward",
                            "name": "origin",
                            "children": list2

                        }
                    })

            print('公司:', sdata)

    def select_son(self, nid):
        self.cursor.execute('select * from buy_business_qccdata_rel where pid=%s' % nid)
        return self.cursor.fetchall()

    def select_father(self, nid):
        self.cursor.execute('select * from buy_business_qccdata_rel where cid=%s' % nid)
        for query in self.cursor.fetchall():
            id = query[1]
            return self.select_data(id)

    def select_data(self, id):
        datadict = {}
        self.cursor.execute('select * from buy_business_qccdata where id=%s' % id)
        data = list(self.cursor.fetchone())[4:-2]
        for i in range(len(data)):
            data[i] = data[i] if data[i] else ''
            datadict[self.key01[i]] = data[i]
        return datadict

    def select_investment(self, id):
        datadict = {}
        self.cursor.execute('select * from buy_business_qcc_investment where id=%s' % id)
        data = list(self.cursor.fetchone())[1:-1]
        for i in range(len(data)):
            data[i] = data[i] if data[i] else ''
            datadict[self.key02[i]] = data[i]
        return datadict

    def rel(self):
        selectsql = 'select id,pid from buy_business_qccdata where level  = 2'
        self.cursor.execute(selectsql)
        getall = self.cursor.fetchall()
        for query in getall:
            cid = query[0]
            pid = query[1]
            sql = 'insert into buy_business_qccdata_rel (cid, pid) values ("%s", "%s")' % (str(pid), str(cid))
            # sql = 'DELETE  FROM  buy_business_qccdata_rel where cid=%s and pid=%s' % (str(pid), str(cid))
            self.cursor.execute(sql)
            self.conn.commit()
            print(cid, pid)


if __name__ == '__main__':
    p = mysql_conn()
    # p.rel()
    p.export_gx()
