import pymysql, copy
from pymysql.converters import escape_string


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '182.92.217.24'
        self.port = 3306
        self.user = 'bidding'
        self.password = 'bidding'
        self.db = 'doc'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        # self.conn_redis = redis_conn()

    ''' 查询采购单位名称不为空、统一社会信用代码为空的字段'''

    def get_purchasing_name(self):
        sql = '''SELECT id, purchasing_name,bidder_name, social_credit_code,purchasing_type ,purchasing_classify FROM bidding_day_data WHERE purchasing_name != '' and social_credit_code is null and parse_result=0 LIMIT 5000'''
        self.cursor.execute(sql)
        fetchall = self.cursor.fetchall()
        print('匹配成功')
        return fetchall

    '''更新数据'''
    def update(self, purchasing_type, social_credit_code, parse_result, purchasing_name):
        sql = '''UPDATE bidding_day_data SET purchasing_type="%s", social_credit_code="%s", parse_result="%s" where purchasing_name="%s"''' % (
        purchasing_type, social_credit_code, parse_result, purchasing_name)
        self.cursor.execute(sql)
        self.conn.commit()
        print(f'更新成功{purchasing_name}:', purchasing_type, social_credit_code, )

    def updateFalse(self,  parse_result, purchasing_name):
        sql = '''UPDATE bidding_day_data SET parse_result="%s" where purchasing_name="%s"''' % (parse_result, purchasing_name)
        self.cursor.execute(sql)
        self.conn.commit()
        print(f'更新失败，未找到:{purchasing_name}')

    def __del__(self):
        self.cursor.close()
        self.conn.close()


if __name__ == '__main__':
    p = pymysql_connection()
    p.get_purchasing_name()
