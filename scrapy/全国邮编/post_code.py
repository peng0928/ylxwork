# -*- coding: utf-8 -*-
# @Date    : 2022-09-28 16:09
# @Author  : chenxuepeng
import requests, pymysql, json
from data_process import *
from lxml import etree
import xlrd

municipality = ['北京市', '天津市', '上海市', '重庆市']  # 直辖市


def xls():
    wb = xlrd.open_workbook('youbian.xls')
    # 按工作簿定位工作表
    sh = wb.sheet_by_name('Sheet1')
    # 遍历excel，打印所有数据
    for i in range(sh.nrows):
        name1 = sh.row_values(i)[0]
        name2 = sh.row_values(i)[1]
        name3 = sh.row_values(i)[2]

        value1 = sh.row_values(i)[3]
        value2 = sh.row_values(i)[4]

        print(name1, name2, name3, value1, value2)
        if name2 in municipality:
            try:
                m_sql(i=4, word=name3, q=value2, c=value1, one=name1)
            except TypeError:
                pass
        else:
            try:
                # m_sql(i=4, word=name3, q=value2, c=value1, one=name1)

                m_sql(i=3, word=name3, q=value2, c=value1, one=name1)
            except TypeError:
                pass


def lost_code():
    with open('./area_division_code.json', 'r', encoding='utf-8')as f:
        p = json.loads(f.read())['RECORDS']
    for item in p:
        cityname = item['name']
        id = item['id']
        code = item['code'].split(',')[0]

        url = f'https://www.nowmsg.com/findzip/cn_youbian_2022.asp?cityname={cityname}'
        response = requests.get(url)
        response.encoding = 'utf-8'
        response_xpath = Xpath(response)
        area_name = response_xpath.xpath("//table[@class='table table-hover']/tbody/tr[1]/td[1]")
        try:
            area_code = response_xpath.xpath("//table[@class='table table-hover']/tbody/tr[1]/td[2]").split(',')[0]

            post_code = response_xpath.xpath("//table[@class='table table-hover']/tbody/tr[1]/td[4]")


            code_name = m_sql(one=code, i=5)[0][:-1].replace('自治', '').replace('壮族', '').replace('维吾尔', '')
            print(area_name, area_code, post_code, code_name, code, id)
            if code_name == area_code:
                m_sql(i=6, c=post_code, one=id)
        except:
            pass

def m_sql(i=None, word=None, q=None, c=None, one=None):
    host = '10.0.3.14'
    port = 3306
    user = 'root'
    password = '123456'
    db = 'doc'
    conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db)
    cursor = conn.cursor()
    if i == 1:
        sql = f"SELECT id FROM area_division_code WHERE `level` = 1 AND name LIKE '%{word}%'"
        cursor.execute(sql)
        id = cursor.fetchone()
        id = id[0]
        up_sql = f'UPDATE area_division_code SET area_code="{q}", post_code="{c}" WHERE id = {id}'
        print(word, q, c)

        cursor.execute(up_sql)
        conn.commit()

    if i == 4:
        sql = f"SELECT id FROM area_division_code WHERE `level` = 1 AND name LIKE '%{one}%'"
        cursor.execute(sql)
        id1 = cursor.fetchone()
        id1 = id1[0]

        sql = f"SELECT id FROM area_division_code WHERE `level` = 2 AND name LIKE '%{word}%' AND `code` like '{id1},%'"
        cursor.execute(sql)
        id = cursor.fetchone()
        id = id[0]
        up_sql = f'UPDATE area_division_code SET area_code="{q}", post_code="{c}" WHERE id = {id}'
        cursor.execute(up_sql)
        conn.commit()
        print(word, q, c)

    if i == 3:
        sql = f"SELECT id FROM area_division_code WHERE `level` = 1 AND name LIKE '%{one}%'"
        cursor.execute(sql)
        id1 = cursor.fetchone()
        id1 = id1[0]

        sql = f"SELECT id FROM area_division_code WHERE `level` = 3 AND name LIKE '%{word}%' AND `code` like '{id1},%'"
        cursor.execute(sql)
        id = cursor.fetchone()
        id = id[0]
        up_sql = f'UPDATE area_division_code SET area_code="{q}", post_code="{c}" WHERE id = {id}'
        cursor.execute(up_sql)
        conn.commit()
        print(word, q, c, id)

    if i == 5:
        sql = f"SELECT name FROM area_division_code WHERE id = '{one}'"
        cursor.execute(sql)
        name = cursor.fetchone()
        return name

    if i == 6:
        up_sql = f'UPDATE area_division_code SET post_code="{c}" WHERE id = {one}'
        cursor.execute(up_sql)
        conn.commit()


    cursor.close()
    conn.close()


if __name__ == '__main__':

    lost_code()
