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
        contenttype = fields['contenttype']
        pagesource = fields['pagesource']
        pagesource = escape_string(pagesource)

        if redis_value is None:
            redis_value = pageurl
        else:
            redis_value = redis_value
        try:
            redis_select_values = redis_value
            sql = 'insert into bidding_day_data_snapshots (host, pageurl, docsubtitle, publishdate, contenttype) value ' \
                  '("%s","%s","%s","%s","%s")' % (host, pageurl, docsubtitle, publishdate, contenttype)

            select_result = self.conn_redis.find_data(value=redis_select_values)
            if select_result is False:
                self.cursor.execute(sql)
                insert_id = self.conn.insert_id()
                self.conn.commit()

                ###################################################
                conn_redis = redis_conn()
                conn_redis.set_add('bidding_www_ccgp_gov_cn', value=pageurl)
                ###################################################

                if contenttype == 0 or contenttype == 2:
                    sql_insert_into_page = f'''insert into bidding_day_data_snapshots_page (id, pagesource)value({insert_id}, '{pagesource}')'''
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

                        self.cursor.execute(sql_insert_into_page)
                        self.conn.commit()


            else:
                print('存在:', pageurl)


        except Exception as e:
            print(e)

    def __del__(self):
        self.cursor.close()
        self.conn.close()
