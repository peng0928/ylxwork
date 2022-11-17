import pymysql, copy, json


class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '10.0.2.248'
        self.port = 3306
        self.user = 'penr'
        self.password = '521014'
        self.db = 'daily_work'
        self.table = 'buy_value_futures'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()

    def insert(self):
        code = [
            '20010101',
            '20010102',
            '20010103',
            '20010104',
            '20010105',
            '20010106',
            '20010107',
            '20010108',
            '20010109',
            '20010110',
            '20010111',
            '20010112',
            '20010113',
            '20010114',
            '20010115',
            '20010116',
            '20010117',
            '20010118',
            '20010119',
            '20010120',
            '20010201',
            '20010202',
            '20010203',
            '20010204',
            '20010205',
            '20010206',
            '20010207',
            '20010208',
            '20010209',
            '20010210',
            '20010211',
            '20010212',
            '20010213',
            '20010214',
            '20010215',
            '20010216',
            '20010217',
            '20010218',
            '20010219',
            '20010220',
            '20010221',
            '20010222',
            '20010223',
            '20010301',
            '20010302',
            '20010303',
            '20010304',
            '20010305',
            '20010306',
            '20010307',
            '20010308',
            '20010309',
            '20010310',
            '20010311',
            '20010312',
            '20010313',
            '20010314',
            '20010315',
            '20010316',
            '20010317',
            '20010318',
            '20010319',
            '20010320',
            '20010321',
        ]
        dic = {
            '01': '日期',
            '02': '交易所',
            '03': '商品名称',
            '04': '合约代码',
            '05': '开盘价',
            '06': '最高价',
            '07': '最低价',
            '08': '收盘价',
            '09': '结算价',
            '10': '昨结算价',
            '11': '涨跌1',
            '12': '涨跌2',
            '13': '成交量',
            '14': '持仓量',
            '15': '持仓量变化',
            '16': '成交额',
        }
        i = 0
        new_json = {}
        for q, y in enumerate(code):
            for k, v in dic.items():
                i += 1
                new_code = y + k
                new_json[new_code] = i
        print(new_json)
        with open('./code.json', 'a')as f:
            f.write(json.dumps(new_json))
        #         sql = 'insert into buy_attribute_futures (attribute_name, alias, parameters_code) value ("%s", "%s", "%s")'%(v, v, new_code)
        #         self.cursor.execute(sql)
        #         self.conn.commit()
        #         print(new_code)


p = pymysql_connection().insert()