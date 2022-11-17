# -*- coding: utf-8 -*-
# @Date    : 2022-11-04 08:55
# @Author  : chenxuepeng
# -*- coding: utf-8 -*-
# @Date    : 2022-10-26 17:13
# @Author  : chenxuepeng
import logging
import os
import re

import requests

from pymysql_connection import *
from useragent import *
from retrying import retry


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
                    "Connection": "keep-alive",
                    "User-Agent": self.ua,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                }
                condition = True  # False：在企查查中匹配到数据; Ture:在企查查未匹配到数据
                search_id = sql_item[0]
                search_key = sql_item[1]
                print('当前: ', search_key)
                search_url = f'https://public.creditchina.gov.cn/private-api/catalogSearchHome?keyword={search_key}&scenes=defaultScenario&tableName=credit_xyzx_tyshxydm&searchState=2&entityType=1%2C2%2C4%2C5%2C6%2C7%2C8&templateId=&page=1&pageSize=10'
                response = self.send_request(url=search_url, headers=headers, proxy={'https': 'tps163.kdlapi.com:15818'})
                response.encoding = 'utf-8'
                '''状态码判断'''
                print(response)
                if str(response.status_code)[0] != '2' or '<title>会员登录' in response.text or '<title>405' in response.text:
                    loginfo = f'Status: False, Status_code: {response.status_code}, url: {search_url}'
                    self.logger.info(loginfo)
                    print('休息一下')
                else:
                    print(response.json())
                    # print(200, search_id)
                    # tree = etree.HTML(response.text)
                    # maininfo = tree.xpath("//div[@class='maininfo']")
                    # for item in maininfo:
                    #     if condition is True:
                    #         company_name = item.xpath(".//span[@class='copy-title']/a[@class='title copy-value']//text()")
                    #         company_name = ''.join(company_name)
                    #         if company_name == search_key:
                    #             social_credit_code = \
                    #             item.xpath(".//span[@class='f'][4]//span[@class='copy-value']//text()")[0]
                    #             purchasing_type = self.purchasing_type_dict[social_credit_code[:2]]
                    #             print(purchasing_type, social_credit_code, search_id)
                    #             # self.p.update(purchasing_type, social_credit_code, 1, search_key)
                    #             # condition = False
                    #     else:
                    #         break
                    # '''企查查未找到'''
                    # if condition is True:
                    #     self.logger.info(f'Not Found:名称 {search_key}; id: {search_id}; url: {search_url}')
                    #     # self.p.updateFalse(2, search_key)

            except Exception as e:
                print(e)

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
        return cookie

    @retry(stop_max_attempt_number=2)
    def send_request(self, methon='GET', url=None, headers=None, proxy=None):
        try:
            response = requests.request(method=methon, url=url, headers=headers, proxies=proxy)
            return response
        except Exception as e:
            raise Exception(e)


if __name__ == '__main__':
    q = QccSpider()
    q.start_request()
