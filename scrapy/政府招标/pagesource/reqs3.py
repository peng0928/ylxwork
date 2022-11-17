# -*- coding: utf-8 -*-
# @Date    : 2022-09-28 09:43
# @Author  : chenxuepeng
import requests, pymysql, json, html, time
from multiprocessing import Pool
from fake_useragent import UserAgent
from pymysql.converters import escape_string


def work(i, page, le):
    # host = i['host']
    # if host == 'zfcg.czt.zj.gov.cn':
        id = i['id']
        pageurl = i['pageurl']
    #     headers = {
    # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    # "Accept-Encoding": "gzip, deflate",
    # "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    # "Cache-Control": "max-age=0",
    # "Connection": "keep-alive",
    # "Cookie": "wzws_cid=2c02774edc7a2d8f098a1e59e4649f013bd9c4a22007477796dbd76eff0f7f8ed3d7dec7afb8abb70c4a9dca0c67abbe9bf2a87fb3866f09d905520e31d01d0758766e9c0d04c6276be1b3873ca726e6",
    # "Host": "www.jl.gov.cn",
    # "If-Modified-Since": "Wed, 30 Sep 2020 07:36:12 GMT",
    # "Referer": "http://www.jl.gov.cn/ggzy/zfcg/cggg/202009/t20200930_7568331.html",
    # "Upgrade-Insecure-Requests": "1",
    # "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
# }
        headers = {}


        try:
            response = requests.get(url=pageurl, headers=headers, proxies={'http': 'tps163.kdlapi.com:15818'})
            # response = requests.get(url=pageurl, headers=headers)
            response.encoding = 'utf-8'
            # noticeContent = json.loads(response.text)['noticeContent']
            response_len = len(response.text)
            if response.status_code == 200 and response_len > 50000:
                print('================', (page / le) * 100, '%====================', page, response_len,  pageurl)
                text = response.text
                # print(response.status_code, response.text)
                mysql_coon(text, id)

            else:
                print('error================', (page / le) * 100, '%====================', pageurl, response.status_code)

        except:
            print('error')

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

if __name__ == '__main__':
    pool = Pool(10)
    with open('./hn.json', 'r')as f:
        obj = f.read()

    objjson = json.loads(obj).get('RECORDS')[19480:]
    le = len(objjson)
    # print(le)
    for page in range(le):
        res = objjson[page]
        # time.sleep(1.5)
        pool.apply_async(work, (res, page, le))

        # 进程池关闭之后不再接受新的请求
    pool.close()
    pool.join()
