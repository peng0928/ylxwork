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

    """第一次数据爬取"""

    def qcc_insert(self, key, value, shareholder=None, investment=None, Type=None, searchName=None):
        """
        :param key: 企业工商信息字段
        :param value: 企业工商信息字段值
        :param shareholder: 股东信息集合
        :param investment: 对外投资集合
        :param searchName:
        :param type:
        :return:
        """
        global shareholder_id, investment_id, insert_id
        try:
            qccdata_table1 = 'buy_business_qccdata'  # 企业名单信息
            if key and value:
                redis_dataname = 'qcc_data'
                findbool = self.conn_redis.find_data(
                    field=redis_dataname, value=searchName)
                if findbool:
                    print('工商数据已存在:', findbool)
                else:
                    data_insert_sql = 'insert into %s (%s) values (%s)' % (
                        qccdata_table1, key, value)
                    self.cursor.execute(data_insert_sql)
                    insert_id = self.conn.insert_id()
                    print(insert_id)
                    # self.conn.commit()
                    data_insert_sql2 = 'UPDATE %s set pid="%s" where id=%s' % (
                        qccdata_table1, insert_id, insert_id)
                    self.cursor.execute(data_insert_sql2)
                    # self.conn.commit()
                    print('工商数据存储成功:', insert_id)

                    # self.conn_redis.set_add(field=redis_dataname, value=searchName)
                    # print('reids 存储成功:', searchName)
            else:
                print('工商数据存储失败:', )
                insert_id = None

            # if insert_id:
            #     "股东信息"
            #     if shareholder:
            #         redsi_name = str(insert_id) + '_' + searchName
            #         print('\033[1;32m正在插入股东信息:\033[0m')
            #         self.insert_shareholderinformation_new(item=shareholder, insert_id=insert_id, redsi_name=redsi_name)
            #         print('完成插入父公司股东信息')
            #
            #     "对外投资"
            #     if investment:
            #         print('\033[1;32m正在插入对外投资: \033[0m')
            #         redsi_name = str(insert_id) + '_' + searchName
            #         tablename = 'buy_business_qcc_investment_new'
            #         findbool = redis_conn().find_data(field=tablename, value=redsi_name)
            #         if findbool:
            #             print('对外投资信息已存在:', redsi_name)
            #         else:
            #             for l in investment:
            #                 StockName = l.get('StockName')
            #                 """子公司"""
            #                 key1 = 'name, pid,  type'
            #                 value1 = f'"{StockName}"' + f',"{insert_id}", "{Type}"'
            #                 shareholder_sql = 'insert into %s (%s) values (%s)' % (qccdata_table1, key1, value1)
            #                 self.cursor.execute(shareholder_sql)
            #                 shareholderid = self.conn.insert_id()
            #                 self.conn.commit()
            #                 self.insert_qcc_investment_new(item=investment, insert_id=insert_id, redsi_name=redsi_name)
            #                 """插入关系"""
            #                 self.cursor.execute('insert into buy_business_qccdata_rel (cid, pid) values ("%s", "%s")' % (shareholderid, insert_id))
            #                 self.conn.commit()
            #             print('完成插入')

        except Exception as e:
            print(e)

    """根据数据库向下爬取"""

    def qcc_insert2(self, litem, ids=None, shareholder=None, investment=None, Type=None, searchName=None):
        insert_id = ids
        global investment_id
        try:
            qccdata_table1 = 'buy_business_qccdata'  # 企业名单信息
            if litem:
                data_insert_sql2 = 'UPDATE %s set %s where id=%s' % (
                    qccdata_table1, litem, ids)
                self.cursor.execute(data_insert_sql2)
                self.conn.commit()
                self.conn_redis.set_add(field='qcc_qccdata', value=searchName)
                print('工商数据 存储成功:', )

            else:
                print('工商数据存储失败:', )

            "股东信息"
            if shareholder:
                redsi_name = str(insert_id) + '_' + searchName
                print('\033[1;32m正在插入股东信息:\033[0m')
                self.insert_shareholderinformation_new(
                    item=shareholder, insert_id=insert_id, redsi_name=redsi_name)
                print('完成插入父公司股东信息')
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
                try:
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
                except Exception as e:
                    print('股东信息:', e)
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

    def t01(self):
        a = ['特力A',
             '富奥股份',
             '潍柴动力',
             '江铃汽车',
             '万向钱潮',
             '海马汽车',
             '威孚高科',
             '贵州轮胎',
             '青岛双星',
             '长安汽车',
             '襄阳轴承',
             '模塑科技',
             '漳州发展',
             '浩物股份',
             '一汽解放',
             '安凯客车',
             '中鼎股份',
             '航天科技',
             '云内动力',
             '钱江摩托',
             '中国重汽',
             '中通客车',
             '众泰汽车股份有限公司',
             '银亿股份',
             '中国中期',
             '铭科精技',
             '宗申动力',
             '巨轮智能',
             '宁波华翔',
             '万丰奥威',
             '广东鸿图',
             '信隆健康',
             '银轮股份',
             '成飞集成',
             '奥特佳',
             '西仪股份',
             '天润工业',
             '亚太股份',
             '新朋股份',
             '兴民智通',
             '隆基机械',
             '远东传动',
             '万里扬',
             '中原内配',
             '松芝股份',
             '双环传动',
             '金固股份',
             '天汽模',
             '旷达科技',
             '飞龙股份',
             '海联金汇',
             '南方精工',
             '万安科技',
             'ST八菱',
             '比亚迪',
             '京威股份',
             '信质集团',
             '浙江世宝',
             '光洋股份',
             '登云股份',
             '跃岭股份',
             '浙农股份',
             '索菱股份',
             '路畅科技',
             '今飞凯达',
             '香山股份',
             '华阳集团',
             '德赛西威',
             '联诚精密',
             '祥鑫科技',
             '森麒麟',
             '征和工业',
             '双林股份',
             '派生科技',
             '美晨生态',
             '精锻科技',
             '云意电气',
             '鹏翎股份',
             '立中集团',
             '富临精工',
             '德尔股份',
             '苏奥传感',
             '川环科技',
             '贝斯特',
             '奥联电子',
             '美力科技',
             '万通智控',
             '雷迪克',
             '隆盛科技',
             '英搏尔',
             '蠡湖股份',
             '兆丰股份',
             '西菱动力',
             '越博动力',
             '欣锐科技',
             '阿尔特',
             '卡倍亿',
             '松原股份',
             '博俊科技',
             '华安鑫创',
             '恒帅股份',
             '东箭科技',
             '致远新能',
             '肇民科技',
             '超捷股份',
             '德迈仕',
             '中集车辆',
             '中捷精工',
             '正强股份',
             '金钟股份',
             '标榜股份',
             '泰祥股份',
             '中汽股份',
             '纽泰格',
             '盛帮股份',
             '东利机械',
             '星源卓镁',
             '东风汽车',
             '宇通客车',
             '东风科技',
             '林海股份',
             '上汽集团',
             '长春一东',
             '航天机电',
             '福田汽车',
             '东安动力',
             'S*ST佳通',
             '亚星客车',
             '全柴动力',
             '广汇汽车',
             'ST曙光',
             '国机汽车',
             '汉马科技',
             '北巴传媒',
             '江淮汽车',
             '风神股份',
             '凌云股份',
             '航天晨光',
             '贵航股份',
             '金杯汽车',
             '申达股份',
             '申华控股',
             '福耀玻璃',
             '交运股份',
             '金龙汽车',
             '湖南天雁',
             '均胜电子',
             '北汽蓝谷',
             '华域汽车',
             '一汽富维',
             '动力新科',
             '爱柯迪',
             '渤海汽车',
             '赛轮轮胎',
             '赛力斯',
             '三角轮胎',
             '广汽集团',
             '庞大集团',
             '英利汽车',
             '通用股份',
             '长城汽车',
             '拓普集团',
             '郑煤机',
             '力帆科技',
             '星宇股份',
             '中国汽研',
             '玲珑轮胎',
             '联明股份',
             '北特科技',
             '亚普股份',
             '威帝股份',
             '常熟汽饰',
             '凯众股份',
             '新坐标',
             '浙江黎明',
             '天成自控',
             '正裕工业',
             '华培动力',
             '春风动力',
             '腾龙股份',
             '科华控股',
             '福达股份',
             '圣龙股份',
             '新泉股份',
             '保隆科技',
             '常润股份',
             '晋拓股份',
             '浙江仙通',
             '天龙股份',
             '日盈电子',
             '旭升集团',
             '华懋科技',
             '湘油泵',
             '迪生力',
             '文灿股份',
             '华达科技',
             '东方时尚',
             '通达电气',
             '爱玛科技',
             '金麒麟',
             '伯特利',
             '朗博科技',
             '德宏股份',
             '岱美股份',
             '秦安股份',
             '隆鑫通用',
             '中马传动',
             '常青股份',
             '科博达',
             '新日股份',
             '宁波高发',
             '豪能股份',
             '合力科技',
             '金鸿顺',
             '铁流股份',
             '雪龙集团',
             '长源东谷',
             '克来机电',
             '泉峰汽车',
             '继峰股份',
             '合兴股份',
             '长华集团',
             '明新旭腾',
             '冠盛股份',
             '上海沿浦',
             '嵘泰股份',
             '西上海',
             '神通科技',
             '天普股份',
             '无锡振华',
             '沪光股份',
             '精进电动',
             '经纬恒润',
             '亿华通',
             '上声电子',
             '菱电电控',
             '九号公司',
             '苏轴股份',
             '泰德股份',
             '安徽凤凰',
             '同心传动',
             '骏创科技',
             '建邦科技',
             '德众汽车',
             '邦德股份',
             '华阳变速',
             '大地电气',
             ]
        for i in a:
            sql = 'select * from buy_business_qccdata where name like ("%s")' % i
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            for q in data:
                print(q)


if __name__ == '__main__':
    p = pymysql_connection().t01()
    # p.get_purchasing_name()
