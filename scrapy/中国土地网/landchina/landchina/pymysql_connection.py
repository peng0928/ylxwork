import pymysql, copy
from .redis_conn import redis_conn


class pymysql_connection():

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

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):
        uuid = fields['uuid']
        del fields['uuid']
        klist = []
        vlist = []
        for k, v in fields.items():
            klist.append(k)
            vlist.append(v)

        av = ['"' + str(i) + '"' for i in vlist]
        k = ','.join(klist)
        v = ','.join(av)

        number = fields['number']  # '宗地编号',
        # xzq = fields['xzq']  # '行政区(内容页)',
        # zdzl = fields['zdzl']  # '土地坐落',
        # tdyt = fields['tdyt']  # '土地用途',
        # crcx = fields['crcx']  # '出让年限',
        # mj = fields['mj']  # '出让面积',
        # rjl = fields['rjl']  # '容积率',
        # jzmd = fields['jzmd']  # '建筑密度',
        # gyfs = fields['gyfs']  # '供应方式',
        # tdjb = fields['tdjb']  # '土地级别',
        # jzmj = fields['jzmj']  # '建筑面积',
        # lhl = fields['lhl']  # '绿化率',
        # jzxg = fields['jzxg']  # '建筑限高',
        # bmjz = fields['bmjz']  # '报名截止时间',
        # bmqs = fields['bmqs']  # '报名起始时间',
        # zpjz = fields['zpjz']  # '招拍挂截止时间',
        # zpqs = fields['zpqs']  # '招拍挂起始时间',
        # crbzj = fields['crbzj']  # '竞买保证金',
        # qsj = fields['qsj']  # '起始价',
        # jjfd = fields['jjfd']  # '加价幅度',
        # cjjg = fields['cjjg']  # '成交价',
        # gsdate = fields['gsdate']  # '成交公示日期',
        # tzqd = fields['tzqd']  # '投资强度',
        # srdw = fields['srdw']  # '受让人',
        # pubdate = fields['fbsj']  # '发布时间',

        sql = 'insert into buy_estate_market (%s) values (%s)' % (k, v)
        try:
            select_result = self.conn_redis.find_data(value=uuid)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入mysql数据库:', insert_id, number)
                self.conn.commit()
                ###################################################
                conn_redis = redis_conn(db=8)
                conn_redis.set_add('buy_estate_market', value=uuid)
                print('正在插入redis数据库:', uuid)
                ###################################################
            else:
                print('已存在:', number)

        except Exception as e:
            print(e, sql)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
