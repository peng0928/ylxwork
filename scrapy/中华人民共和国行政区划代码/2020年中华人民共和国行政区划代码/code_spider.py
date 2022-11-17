# -*- coding: utf-8 -*-
# @Date    : 2022-09-26 10:06
# @Author  : chenxuepeng
import requests, pymysql
from data_process import *
from lxml import etree


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

    def spider(self):
        global pid, all
        all = 9
        dj = 0
        pid1 = 0
        pid2 = 0
        pid22 = 0
        url = 'https://www.mca.gov.cn/article/sj/xzqh/2020/20201201.html'
        response = requests.get(url)
        objection = etree.HTML(response.text)
        objection = objection.xpath("//table//tr")

        # for i in range(len(code)):

        for i in objection:
            code = process_text(i.xpath(".//td[2]//text()"))
            city = process_text(i.xpath(".//td[3]//text()"))

            if code is None:
                pass
            else:
                try:

                    if int(code) % 100 == 0:
                        all += 1
                        if int(code) % 10000 == 0:
                            pid1 = all
                            code, city, dj, pid = code, city, 1, pid1
                        else:
                            pid2 = pid1
                            pid22 = all
                            code, city, dj, pid = code, city, 2, str(pid2) + ',' + str(all)

                    else:
                        if '110' in code[:3] or '120' in code[:3] or '310' in code[:3] or '500' in code[:3]:
                            all += 1
                            pidd = pid1
                            pid22 = str(pidd) + ',' + str(all)
                            code, city, dj, pid = code, city, 2, pid22
                        else:
                            all += 1

                            pid3 = str(pid1) + ',' + str(pid22) + ',' + str(all)
                            code, city, dj, pid = code, city, 3, pid3

                    sql = f'insert into area_division_code (id, ind_code, name, level, code, effective_date) values ("{all}","{code}", "{city}", "{dj}", "{pid}", "2020-05-10")'
                    self.cursor.execute(sql)
                    self.conn.commit()
                    print(all, code, city, dj, pid)
                except:
                    pass


if __name__ == '__main__':
    pymysql_connection().spider()
