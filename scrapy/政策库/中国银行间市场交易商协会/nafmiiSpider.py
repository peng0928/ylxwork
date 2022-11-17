# -*- coding: utf-8 -*-
# @Date    : 2022-11-08 11:08
# @Author  : chenxuepeng
import requests, pymysql, uuid, os, logging
from data_process import *
from useragent import *
from pymysql_connection import *


class MainSpider(object):

    def __init__(self):
        self.logger = self.log()
        self.start_url = 'http://www.nafmii.org.cn/zlgl/zlcf/zlcfgl/index.html'
        self.start_page = 85  # 爬取总页数
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Host": "www.nafmii.org.cn",
            "Referer": "http: //www.nafmii.org.cn/zlgl/zlcf/zlcfgl/index.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": get_ua()
        }
        self.p = pymysql_connection()
        self.nextpage = True  # 去重开关
        self.orgnike = pymsysql_109().bank_orgnike()

    def start_request(self):
        for page in range(0, self.start_page):
            print(page)
            if page > 0:
                url = self.start_url.replace('index', f'index_{page}')
            else:
                url = self.start_url
            if self.nextpage:
                try:
                    response = requests.get(url=url, headers=self.headers)
                    self.lparse(response)
                except Exception as e:
                    self.logger.info(e)
                    print(e)
            else:
                print('已存在, 退出下一页.')
                break

    def lparse(self, response):
        conn = redis_conn()
        response.encoding = 'utf-8'
        obj = Xpath(response.text)
        titles = obj.xpath("//td[@class='right_data'][5]/a", is_list=True)
        links = obj.xpath("//td[@class='right_data'][5]/a/@href", is_list=True)
        pbdate = obj.xpath("//td[@class='right_data'][4]", is_list=True)
        links = ['http://www.nafmii.org.cn/zlgl/zlcf/zlcfgl' + i[1:] for i in links]
        for li in range(len(links)):
            title = titles[li].replace('—', '——').replace('--', '——').split('——')[-1]
            if re.search('\d', title) and '——' not in title:
                pass
            else:
                # 去重唯一标识: uuid
                uuid_str = links[li] + title + pbdate[li]
                uuids = uuid.uuid3(uuid.NAMESPACE_DNS, uuid_str)
                meta = {
                    'pbdate': pbdate[li],
                    'title': title,
                    'uuid_str': uuids,
                }
                result = conn.find_data(field='risk_day_data_snapshots_nafmii:', value=str(uuids))
                if result is False:
                    response = requests.get(url=links[li], headers=self.headers)
                    self.cparse(response, meta)
                else:
                    print('已存在:', title)
                    self.nextpage = False

    def cparse(self, response, meta):
        item = {}
        response.encoding = 'utf-8'
        obj = Xpath(response.text)
        content = obj.xpath("//div[@class='yh_viewTextBox']", character=False)
        content = self.replace(content)
        pub_date = meta.get('pbdate', '')
        pageurl = response.url
        bank_name = re.findall('决定）(.*?)（以下简称', content)
        if not bank_name:
            bank_name = re.findall('(.*?)（以下简称', content)
            bank_name = bank_name[0] if bank_name else []
            bank_name = bank_name.split('）')[-1] if '）' in bank_name else bank_name
            bank_name = bank_name.split('，')[-1] if '，' in bank_name else bank_name
            if bank_name != []:
                bank_name = bank_name.replace('　　', '')
                bank_name = re.findall('\d([\u4e00-\u9fa5]+)', bank_name)[0] if re.search('\d',
                                                                                          bank_name) else bank_name
        else:
            bank_name = bank_name[0].strip()

        bank_abbreviation = re.findall('以下简称“(.*?)”', content)
        bank_abbreviation = bank_abbreviation[0] if bank_abbreviation else []

        cause_rule = '(.*?)(根据银行间债券市场相关自律规定|依据相关自律规定)'
        cause = re.findall(cause_rule, content)
        cause = cause[0][0] if cause else []
        decision_rule = '(根据银行间债券市场相关自律规定.*|依据相关自律规定.*)'
        decision = re.findall(decision_rule, content)
        decision = decision[0] if decision else []

        item['pageurl'] = pageurl
        item['pub_date'] = pub_date
        item['bank_name'] = bank_name
        item['bank_abbreviation'] = bank_abbreviation
        item['cause'] = cause
        item['decision'] = decision
        item['uuid'] = str(meta.get('uuid_str', ''))

        condition = self.box(item)  # 判定字段缺失不入库
        if condition:
            if bank_abbreviation in self.orgnike:
                self.p.insert_into_doc(fields=item)  # 判断是否属于银行
                self.logger.info('银行:' + bank_abbreviation + ' 位置:' + pageurl)
            else:
                self.logger.info('非银行:' + bank_abbreviation + ' 位置:' + pageurl)

    def replace(self, text):
        text = text.replace(')', '）').replace('(', '（')
        return text

    def box(self, item):
        C = True
        for k, v in item.items():
            if len(v) <= 0:
                C = False
        return C

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

    def __del__(self):
        self.p.close()


if __name__ == '__main__':
    MainSpider().start_request()
