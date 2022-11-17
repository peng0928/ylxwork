import pymysql, copy
from .redis_conn import redis_conn
from pymysql.converters import escape_string

class pymysql_connection():

    # ssh mysql
    def __init__(self):
        self.host = '172.17.199.146'
        self.port = 3306
        self.user = 'bidding'
        self.password = 'bidding'
        self.db = 'doc'
        # self.db = 'daily_work'
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                    database=self.db)
        self.cursor = self.conn.cursor()
        self.conn_redis = redis_conn()

    def insert_into_doc(self, fields=None, tablename=None, redis_field=None, redis_value=None):
        if 'filelink' in fields:
            filelink = fields['filelink']
            filename = fields['filename']
        else:
            filelink = None
            filename = None
        host = fields['host']
        pageurl = fields['pageurl']
        docsubtitle = fields['docsubtitle']
        publishdate = fields['publishdate']
        pagesource = fields['pagesource']
        pagesource = escape_string(pagesource)
        contenttype = fields['contenttype']
        type = fields['type']

        if redis_value is None:
            redis_value = pageurl
        else:
            redis_value = redis_value
        try:
            redis_select_values = pageurl
            sql = 'insert into bidding_day_data_snapshots (host, pageurl, docsubtitle, publishdate, contenttype, type) value ' \
                  '("%s","%s","%s","%s","%s","%s")' % (host, pageurl, docsubtitle, publishdate, contenttype, type)

            select_result = self.conn_redis.find_data(value=redis_select_values)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                print(f'正在插入数据库{insert_id}:', docsubtitle, pageurl)
                self.conn.commit()

                ###################################################
                conn_redis = redis_conn()
                conn_redis.set_add('bidding', value=pageurl)
                ###################################################

                if contenttype == 0 or contenttype == 2:
                    sql_insert_into_page = f'''insert into bidding_day_data_snapshots_page (id,pagesource)value({insert_id},'{pagesource}')'''
                    print(f'page:', insert_id)
                    self.cursor.execute(sql_insert_into_page)
                    self.conn.commit()

                # 存储文件
                if filename is not None and filelink is not None:
                    names = filename.split('|')
                    links = filelink.split('|')
                    for i in range(len(names)):
                        name = names[i]
                        link = links[i]
                        sql_insert_into_page = f'''insert into bidding_day_data_snapshots_file (id,filename,filelink)value({insert_id},'{name}','{link}')'''
                        print(f'file:', name, link)
                        self.cursor.execute(sql_insert_into_page)
                        self.conn.commit()

                # reids断点
                if redis_field != None:
                    self.conn_redis.del_data(field=redis_field, value=redis_value)

            else:
                print('已存在:', sql)
                if redis_field != None:
                    self.conn_redis.del_data(field=redis_field, value=redis_value)

        except Exception as e:
            print(e)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
