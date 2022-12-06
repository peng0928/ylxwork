import math, json, uuid
import scrapy
from ..data_process import *
from ..decorator_penr import *
from ..redis_conn import *


class SpiderSpider(scrapy.Spider):
    """中国土地市场网"""
    name = "spider"
    starturl = "https://api.landchina.com/tGyggZd/transfer/list"
    headers = {
        "Content-Type": "application/json",
        "Hash": "c8d93e43c5c8a0cdea12496e81e155cd3aff48b7ddb248128911bde975498a35",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
    start_time = "2022-01-01 00:00:00"
    end_time = f"{get_datetime_now()} 23:59:59"
    req_data = '{"pageNum": 1, "pageSize": 10, "startDate": "%s", "endDate": "%s"}' % (
        start_time, end_time)

    def start_requests(self):
        ii = int(input(':'))

        for i in range(ii, 8651):
            data = self.req_data.replace('pageNum": 1', f'pageNum": {i}')
            print(data)
            yield scrapy.Request(url=self.starturl, method='POST', headers=self.headers, body=data, meta={"page": i},
                                 callback=self.lparse
                                 )

    def get_page(self, response):
        obj = response.json()
        data = obj.get('data')
        if data:
            total = data.get('total')
            page = math.ceil(total / 10)  # 2022-01-01到至今
            print(page)
            for i in range(1500, page + 1):
                data = self.req_data.replace('pageNum": 1', f'pageNum": {i}')
                yield scrapy.Request(url=self.starturl, method='POST', headers=self.headers, dont_filter=True,
                                     body=data, callback=self.lparse, meta={"page": i})

    def lparse(self, response):
        print('当前页: ', response.meta['page'])
        item = {}
        reconn = redis_conn()
        obj = response.json()
        data = obj.get('data')
        total = data.get('total')
        if total < 86508:
            print(data)
            if data:
                list = data.get('list')
                for i in list:
                    xzqFullName = i.get('xzqFullName')  # 行政区
                    zdh = i.get('zdBh')  # 宗地编号
                    zdZl = i.get('zdZl')  # 土地坐落
                    mj = i.get('mj')  # 总面积(平方米)
                    tdYt = i.get('tdYt')  # 土地用途
                    gyFs = i.get('gyFs')  # 供应方式
                    fbSj = i.get('fbSj')  # 发布时间
                    gyggZdGuid = i.get('gyggZdGuid')  # 发布时间

                    item['xzqFullName'] = xzqFullName
                    item['zdh'] = zdh
                    item['zdZl'] = zdZl
                    item['mj'] = mj
                    item['tdYt'] = tdYt
                    item['gyFs'] = gyFs
                    item['fbSj'] = fbSj.replace('T', ' ')

                    uuid_str = str(item)
                    item_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, uuid_str)
                    item['uuid'] = str(item_uuid.hex)
                    # print(item)

                    curl = 'https://api.landchina.com/tGyggZd/land/detail'
                    cdata = '{"landType":1,"landGuid":"%s"}' % gyggZdGuid
                    print(cdata)
                    select_result = reconn.find_data(value=item['uuid'])
                    if select_result is False:
                        yield scrapy.Request(url=curl, method='POST', headers=self.headers, dont_filter=True,
                                             body=cdata,
                                             callback=self.cparse, meta=item)
                    else:
                        print('已存在', item_uuid)
        else:
            print('休息60s')
            time.sleep(60)
            raise ValueError('休息60s')

    def cparse(self, response):
        data = response.json().get('data')
        citem = {}
        if data:
            zdh = response.meta['zdh']  # 宗地编号
            uuid = response.meta['uuid']  # uuid
            fbsj = response.meta['fbSj']  # 发布时间
            xzq = data.get('xzqFullName')  # 行政区
            zdzl = data.get('zdZl')  # 土地坐落
            tdyt = data.get('tdYt')  # 土地用途
            crcx = data.get('crNx')  # 出让年限
            mj = str(data.get('mj'))  # 出让面积
            citem['xzq'] = xzq
            citem['zdzl'] = zdzl
            citem['tdyt'] = tdyt
            citem['crcx'] = crcx
            citem['mj'] = mj
            citem['number'] = zdh
            citem['pubdate'] = fbsj
            citem['uuid'] = uuid

            maxRjl = data.get('maxRjl') if data.get('maxRjlTag') else None
            minRjl = data.get('minRjl') if data.get('minRjlTag') else None
            rjl = self.msg(n='容积率', n1=maxRjl, n2=minRjl, )
            citem['rjl'] = rjl

            maxJzMd = data.get('maxJzMd') if data.get('maxJzMdTag') else None
            minJzMd = data.get('minJzMd') if data.get('minJzMdTag') else None
            jzmd = self.msg(n='建筑密度', n1=maxJzMd, n2=minJzMd, n3='%')
            citem['jzmd'] = jzmd

            gyfs = data.get('gyFs')  # 供应方式
            tdjb = data.get('tdJb', '--')  # 土地级别
            jzmj = data.get('jzMj', '--')  # 建筑面积
            citem['gyfs'] = gyfs
            citem['tdjb'] = tdjb
            citem['jzmj'] = jzmj

            maxlhl = data.get('maxLhl') if data.get('manLhlTag') else None
            minlhl = data.get('minLhl') if data.get('minLhlTag') else None
            lhl = self.msg(n='绿化率', n1=maxlhl, n2=minlhl, n3='%')
            citem['lhl'] = lhl

            maxjzxg = data.get('maxJzXg') if data.get('maxJzXgTag') else None
            minjzxg = data.get('minJzXg') if data.get('minJzXgTag') else None
            jzxg = self.msg(n='建筑限高', n1=maxjzxg, n2=minjzxg, n3='米')
            citem['jzxg'] = jzxg

            bmjz = data.get('tjSqSjE', '--')  # 报名截止时间
            bmqs = data.get('tjSqSjS', '--')  # 报名起始时间
            citem['bmjz'] = process_timestamp(bmjz)
            citem['bmqs'] = process_timestamp(bmqs)

            zpjz = data.get('gpSjE', '--')  # 招拍挂截止时间
            zpqs = data.get('gpSjS', '--')  # 招拍挂起始时间
            citem['zpjz'] = process_timestamp(zpjz)
            citem['zpqs'] = process_timestamp(zpqs)

            crBzj = data.get('crBzj', '--')  # 竞买保证金 单位：万元
            citem['crbzj'] = str(crBzj) if crBzj and crBzj != '--' else crBzj

            qsj = data.get('qsj', '--')  # 起始价
            qsjDw = data.get('qsjDw')  # 起始价单位：万元
            citem['qsj'] = str(qsj) if qsj and qsj != '--' else qsj

            jjFd = data.get('jjFd', '--')  # 加价幅度
            jjfdDw = data.get('jjfdDw')  # 加价幅度单位：万元
            citem['jjfd'] = str(jjFd) if jjFd and jjFd != '--' else jjFd

            cjJg = data.get('cjJg', '--')  # 成交价 单位：万元
            citem['cjjg'] = str(cjJg) if cjJg and cjJg != '--' else cjJg

            gs_sdate = data.get('gsSjE', '--')
            gs_edate = data.get('gsSjS', '--')
            gs_date = gs_edate  # 成交公示日期
            citem['gsdate'] = gs_date

            tzQd = data.get('tzQd', '--')  # 投资强度 单位：万元/公顷
            tzQd = '--' if tzQd == 0 else tzQd
            srDw = data.get('srDw', '--')  # 受让人
            citem['tzqd'] = str(tzQd) if tzQd and tzQd != '--' else tzQd
            citem['srdw'] = srDw
            try:
                citem['price'] = '%.2f'%(cjJg/jzmj)
            except:
                pass

            if zdzl is None:
                print('休息60s')
                time.sleep(60)
                raise ValueError('休息60s')
            else:
                # pass
                # print(citem)
                yield citem

    def msg(self, n, n1, n2, n3=''):
        n1 = str(n1) if n1 else None
        n2 = str(n2) if n2 else None
        obj1 = '≤' + n1 + n3 if n1 else ''
        obj2 = n2 + n3 + '≤' if n2 else ''
        obj1 = obj1.replace('≤', '') if '--' in obj1 else obj1
        obj2 = obj2.replace('≤', '') if '--' in obj2 else obj2
        obj = obj2 + f' {n} ' + obj1
        return obj
