# -*- coding: utf-8 -*-
# @Date    : 2022-10-26 17:13
# @Author  : chenxuepeng
import logging
import os
import re

import requests
from lxml import etree

from pymysql_connection import *
from useragent import *



class QccSpider:

    def __init__(self):
        self.logger = self.log()
        self.p = pymysql_connection()
        self.purchasing_type_dict = {'11': '机关',
                                     '12': '事业单位',
                                     '13': '编办直接管理机构编制的群众团体',
                                     '19': '其他',
                                     '21': '外国常驻新闻机构',
                                     '29': '其他',
                                     '31': '律师执业机构',
                                     '32': '公证处',
                                     '33': '基层法律服务所',
                                     '34': '司法鉴定机构',
                                     '35': '仲裁委员会',
                                     '39': '其他',
                                     '41': '外国在华文化中心',
                                     '49': '其他',
                                     '51': '社会团体',
                                     '52': '民办非企业单位',
                                     '53': '基金会',
                                     '59': '其他',
                                     '61': '外国旅游部门常驻代表机构',
                                     '62': '港澳台地区旅游部门常驻内地(大陆)代表 机构',
                                     '69': '其他',
                                     '71': '宗教活动场所',
                                     '72': '宗教院校',
                                     '79': '其他',
                                     '81': '基层工会',
                                     '89': '其他',
                                     '91': '企业',
                                     '92': '个体工商户',
                                     '93': '农民专业合作社',
                                     'A1': '军队事业单位',
                                     'A9': '其他',
                                     'N1': '组级集体经济组织',
                                     'N2': '村级集体经济组织',
                                     'N3': '乡镇级集体经济组织',
                                     'N9': '其他',
                                     'Y1': '其他', }
        self.ua = get_ua()


    def start_request(self):
        sql_list = []
        sql_list2 = []
        sql_result = self.p.get_purchasing_name()
        '''数据查询去重-去除重复采购单位'''
        for i in sql_result:
            if i[1] not in sql_list2:
                sql_list.append(list(i))
                sql_list2.append(i[1])
        for sql_item in sql_list:
            try:
                headers = {
                    # "Host": "www.qcc.com",
                    "Connection": "keep-alive",
                    "User-Agent": self.ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Referer": "https://www.qcc.com/web/search?key=",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    # "cookie": self.get_cookie()
                    "cookie": 'acw_tc=deba129a16678086891534339e20fb98d33a744c9f1b9f2c3af7b3cc22; QCCSESSID=588fa241742fb8f0f95151f18b'
                }
                condition = True  # False：在企查查中匹配到数据; Ture:在企查查未匹配到数据
                search_id = sql_item[0]
                search_key = sql_item[1]
                print('当前: ', search_key)
                search_url = f'https://www.qcc.com/web/search?key={search_key}'
                response = requests.get(search_url, headers=headers, timeout=10, proxies={'https': 'tps163.kdlapi.com:15818'})
                response.encoding = 'utf-8'
                '''状态码判断'''
                if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                    error_msg = re.findall('(<title>.*?</title>)', response.text)[0]
                    loginfo = f'Status: False, Status_code: {response.status_code}, url: {search_url}, msg: {error_msg}'
                    self.logger.info(loginfo)
                    print('未成功: ', error_msg)

                else:
                    print(200, search_id, search_url)
                    tree = etree.HTML(response.text)
                    maininfo = tree.xpath("//div[@class='maininfo']")
                    for item in maininfo:
                        if condition is True:
                            company_name = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']//text()")
                            company_name = ''.join(company_name)
                            if company_name == search_key:
                                social_credit_code = item.xpath(".//span[@class='f'][4]//span[@class='copy-value']//text()")[0]
                                try:
                                    purchasing_type = self.purchasing_type_dict[social_credit_code[:2]]
                                    self.p.update(purchasing_type, social_credit_code, 1, search_key)
                                    condition = False
                                except:
                                    self.logger.info(f'信用代码未匹配成功:名称 {search_key}; id: {search_id}; social_credit_code: {social_credit_code}')
                                    print(f'信用代码未匹配成功: {social_credit_code}')
                        else:
                            break
                    '''企查查未找到'''
                    if condition is True:
                        self.logger.info(f'Not Found:名称 {search_key}; id: {search_id}; url: {search_url}')
                        self.p.updateFalse(2, search_key)

                    print('\n')

            except Exception as e:
                print('\n')
                print(e)
            # timenum = random.randint(1, 5)
            # print('本次休眠:', timenum)
            # time.sleep(timenum)

    def log(self):
        os.makedirs('./loging', exist_ok=True)
        logger = logging.getLogger(__name__)
        logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler("./loging/log.txt")
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def get_cookie(self):
        url = 'https://www.qcc.com/ '
        headers = {
            "Host": "www.qcc.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        response = requests.get(url=url, headers=headers, timeout=10, proxies={'https': 'tps163.kdlapi.com:15818'})
        Set_Cookie = response.headers.get('Set-Cookie')
        get_keys = re.findall('(acw_tc|QCCSESSID)(.*?);', Set_Cookie)
        cookies = [''.join(i) for i in get_keys]
        cookie = '; '.join(cookies)
        print(cookie)
        return cookie


if __name__ == '__main__':
    q = QccSpider()
    q.start_request()
