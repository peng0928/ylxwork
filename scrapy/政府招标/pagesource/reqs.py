# -*- coding: utf-8 -*-
# @Date    : 2022-09-28 09:43
# @Author  : chenxuepeng
import requests, pymysql, json, html
from multiprocessing import Pool
from fake_useragent import UserAgent
from pymysql.converters import escape_string

def work(i, page, le, s):
    id = i['id']
    pageurl = i['pageurl']
    host = i['host']

    headers = {'user-agent': UserAgent().random}
    s.append(host)

    print(s)

    # response = requests.get(url=pageurl, headers=headers)
    # if response.status_code == 200:
    #     response.encoding = 'utf-8'
    #     print('================', (page / le) * 100, '%====================', page)
    #     text = html.unescape(response.text)
    #     mysql_coon(text, id)
    #
    # else:
    #     print('================', (page / le) * 100, '%====================')
    #     error(pageurl)
    #     pass


def mysql_coon(pagesource, i):
    pagesource = escape_string(pagesource)
    host = '182.92.217.24'
    port = 3306
    user = 'bidding'
    password = 'bidding'
    db = 'doc'
    # self.db = 'daily_work'
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db)
    cursor = conn.cursor()
    sql_insert_into_page = f'''UPDATE bidding_day_data_snapshots_page SET pagesource = "%s" WHERE id = "%s"''' % (
    pagesource, i)
    cursor.execute(sql_insert_into_page)
    conn.commit()
    print(f'update-page:', i)
    cursor.close()
    conn.close()

def error(word):
    with open('./error.txt', 'a')as f:
        f.write(word+'\n')


if __name__ == '__main__':
    # limit = 0
    # pool = Pool(5)
    #
    # for page in range(29115):
    #     print('================', (page/29115)*100 ,'%====================')
    #     res = mysql_coon(limit)
    #     for i in range(len(res)):
    #         pool.apply_async(work, (res[i],))
    #     # 进程池关闭之后不再接受新的请求
    #     limit += 100
    # pool.close()
    # pool.join()
    pool = Pool(10)
    s = []
    with open('./page_null.json', 'r')as f:
        obj = f.read()

    objjson = json.loads(obj).get('RECORDS')[:]
    for i in objjson:
        host = i['host']
        s.append(host)
    s = set(s)
    print(s)
    # le = len(objjson)
    # print(le)
    # for page in range(le):
    #     res = objjson[page]
    #     pool.apply_async(work, (res, page, le, s))
    #     # 进程池关闭之后不再接受新的请求
    #
    # pool.close()
    # pool.join()
