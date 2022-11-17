import pymysql
import xlrd


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.3.14'
        self.port = 3306
        self.user = 'root'
        # self.password = 'Windows!@#'
        self.password = '123456'
        self.db = 'doc'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):
        global id, gid, cid

        gid = 0
        cid = 0

        data = xlrd.open_workbook('./工作簿1.xls')  # 打开xls文件
        table = data.sheets()[0]  # 打开第一张表
        nrows = table.nrows  # 获取表的行数
        for i in range(nrows):  # 循环逐行打印
            if i == 0:  # 跳过第一行
                continue
            row_values = table.row_values(i)  # 取前十三列

            if row_values[0] != '':
                print(row_values)
                pid = 0
                for item in range(len(row_values)):
                    print(item)
                    if item == 0:
                        sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                            row_values[item], pid)
                        self.cursor.execute(sql)
                        id = self.conn.insert_id()
                        gid = self.conn.insert_id()
                        print(sql)
                        self.conn.commit()

                    if item == 1:
                        sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                            row_values[item], gid)
                        self.cursor.execute(sql)
                        id = self.conn.insert_id()
                        cid = self.conn.insert_id()
                        print(sql)
                        self.conn.commit()

                    if item > 1:
                        sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                            row_values[item], id)
                        self.cursor.execute(sql)
                        id = self.conn.insert_id()
                        print(sql)
                        self.conn.commit()
            else:
                print(row_values)
                if row_values[1] != '':
                    for item in range(1, len(row_values)):
                        if item == 1:
                            sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                                row_values[item], gid)
                            self.cursor.execute(sql)
                            id = self.conn.insert_id()
                            cid = self.conn.insert_id()
                            print(sql)
                            self.conn.commit()

                        else:
                            sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                                row_values[item], id)
                            self.cursor.execute(sql)
                            id = self.conn.insert_id()
                            print(sql)

                            self.conn.commit()
                else:
                    for item in range(1, len(row_values)):
                        if item == 2:
                            sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                                row_values[item], cid)
                            self.cursor.execute(sql)
                            id = self.conn.insert_id()
                            self.conn.commit()
                            print(sql)

                        if item == 3:
                            sql = 'insert into green_finance_cause_type(cause_type, pid) value ("%s",%d)' % (
                                row_values[item], id)
                            self.cursor.execute(sql)
                            id = self.conn.insert_id()
                            self.conn.commit()
                            print(sql)


def excel():
    pid = -7
    data = xlrd.open_workbook('./企业生态环境污染事由分类.xls')  # 打开xls文件
    table = data.sheets()[0]  # 打开第一张表
    nrows = table.nrows  # 获取表的行数
    for i in range(nrows):  # 循环逐行打印
        if i == 0:  # 跳过第一行
            continue
        row_values = table.row_values(i)  # 取前十三列

        if row_values[0] != '':
            pid += 1
            print(pid, row_values)
        else:
            print(row_values)


if __name__ == '__main__':
    p = pymysql_connection()
    p.insert_into_doc()
