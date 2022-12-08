# -*- coding: utf-8 -*-
# @Date    : 2022-12-07 08:54
# @Author  : chenxuepeng
import requests, uuid
from landchina.data_process import *
from landchina.decorator_penr import *
from landchina.redis_conn import *
from landchina.pymysql_connection import *


class Spider:
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

    def start_request(self):
        ii = int(input(':'))
        for i in range(ii, 8651):
            print(f'当前页:{i}')

            """列表页"""
            self.lparse(i)

    @retry(exceptions=True, max_retries=8, delay=1)
    def lparse(self, i):
        data = self.req_data.replace('pageNum": 1', f'pageNum": {i}')
        response = requests.post(url=self.starturl, headers=self.headers, data=data,
                                 proxies={'https': 'tps163.kdlapi.com:15818'})
        obj = response.json()
        reconn = redis_conn()
        data = obj.get('data')
        total = data.get('total')
        item = {}
        if total < 90000:
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

                    curl = 'https://api.landchina.com/tGyggZd/land/detail'
                    cdata = '{"landType":1,"landGuid":"%s"}' % gyggZdGuid
                    select_result = reconn.find_data(value=item['uuid'])
                    if select_result is False:
                        """内容页"""

                        self.cparse(curl=curl, cdata=cdata, item=item)

                    else:
                        print('已存在', item_uuid)


        else:
            print(total)
            raise ValueError('列表访问失败')

    @retry(exceptions=True, max_retries=8, delay=3)
    def cparse(self, curl, cdata, item):
        response = requests.post(url=curl, headers=self.headers, data=cdata,
                                 proxies={'https': 'tps163.kdlapi.com:15818'})
        data = response.json().get('data')
        citem = {}
        if data:
            zdh = item['zdh']  # 宗地编号
            uuid = item['uuid']  # uuid
            fbsj = item['fbSj']  # 发布时间
            xzq = data.get('xzqFullName')  # 行政区
            zdzl = data.get('zdZl')  # 土地坐落
            tdyt = data.get('tdYt')  # 土地用途
            crcx = data.get('crNx')  # 出让年限
            mj = str(data.get('mj'))  # 出让面积
            citem['1'] = zdh
            citem['2'] = xzq
            citem['3'] = zdzl
            citem['4'] = tdyt
            citem['5'] = crcx
            citem['6'] = mj

            maxRjl = data.get('maxRjl') if data.get('maxRjlTag') else None
            minRjl = data.get('minRjl') if data.get('minRjlTag') else None
            rjl = self.msg(n='容积率', n1=maxRjl, n2=minRjl, )
            citem['7'] = rjl

            maxJzMd = data.get('maxJzMd') if data.get('maxJzMdTag') else None
            minJzMd = data.get('minJzMd') if data.get('minJzMdTag') else None
            jzmd = self.msg(n='建筑密度', n1=maxJzMd, n2=minJzMd, n3='%')
            citem['8'] = jzmd

            gyfs = data.get('gyFs')  # 供应方式
            tdjb = data.get('tdJb', '--')  # 土地级别
            jzmj = data.get('jzMj', '--')  # 建筑面积
            citem['9'] = gyfs
            citem['10'] = tdjb
            citem['11'] = jzmj

            maxlhl = data.get('maxLhl') if data.get('manLhlTag') else None
            minlhl = data.get('minLhl') if data.get('minLhlTag') else None
            lhl = self.msg(n='绿化率', n1=maxlhl, n2=minlhl, n3='%')
            citem['12'] = lhl

            maxjzxg = data.get('maxJzXg') if data.get('maxJzXgTag') else None
            minjzxg = data.get('minJzXg') if data.get('minJzXgTag') else None
            jzxg = self.msg(n='建筑限高', n1=maxjzxg, n2=minjzxg, n3='米')
            citem['13'] = jzxg

            bmjz = data.get('tjSqSjE', '--')  # 报名截止时间
            bmqs = data.get('tjSqSjS', '--')  # 报名起始时间
            citem['14'] = process_timestamp(bmjz)
            citem['15'] = process_timestamp(bmqs)

            zpjz = data.get('gpSjE', '--')  # 招拍挂截止时间
            zpqs = data.get('gpSjS', '--')  # 招拍挂起始时间
            citem['16'] = process_timestamp(zpjz)
            citem['17'] = process_timestamp(zpqs)

            crBzj = data.get('crBzj', '--')  # 竞买保证金 单位：万元
            citem['18'] = str(crBzj) if crBzj and crBzj != '--' else crBzj

            qsj = data.get('qsj', '--')  # 起始价
            qsjDw = data.get('qsjDw')  # 起始价单位：万元
            citem['19'] = str(qsj) if qsj and qsj != '--' else qsj

            jjFd = data.get('jjFd', '--')  # 加价幅度
            jjfdDw = data.get('jjfdDw')  # 加价幅度单位：万元
            citem['20'] = str(jjFd) if jjFd and jjFd != '--' else jjFd

            cjJg = data.get('cjJg', '--')  # 成交价 单位：万元
            citem['21'] = str(cjJg) if cjJg and cjJg != '--' else cjJg

            gs_sdate = data.get('gsSjE', '--')
            gs_edate = data.get('gsSjS', '--')
            gs_date = gs_edate  # 成交公示日期
            citem['22'] = gs_date

            tzQd = data.get('tzQd', '--')  # 投资强度 单位：万元/公顷
            tzQd = '--' if tzQd == 0 else tzQd
            srDw = data.get('srDw', '--')  # 受让人
            citem['23'] = str(tzQd) if tzQd and tzQd != '--' else tzQd
            citem['24'] = srDw
            citem['25'] = fbsj
            try:
                citem['26'] = '%.2f' % (cjJg / jzmj)
            except:
                citem['26'] = ''
            qdRq = data.get('qdRq', '')  # 合同签订日期
            xmMc = data.get('xmMc', '')  # 项目名称
            bh = data.get('bh', '')  # 合同编号
            hyFl = data.get('hyFl', '')  # 行业分类
            jdSj = data.get('jdSj', '')  # 约定交地时间
            jgSj = data.get('jgSj', '')  # 约定竣工时间
            tdLy = data.get('tdLy', '')  # 土地来源
            tdSyqr = data.get('tdSyqr', '')  # 土地使用权人
            dzBaBh = data.get('dzBaBh', '')  # 电子监管号
            crjZfydList = data.get('crjZfydList', '')
            if crjZfydList:
                zfSj = crjZfydList[0].get('zfSj') # 约定支付日期
                zfJe = crjZfydList[0].get('zfJe') # 约定支付日期
            else:
                zfSj = ''
                zfJe = ''
            citem['27'] = qdRq
            citem['28'] = xmMc
            citem['29'] = bh
            citem['30'] = hyFl
            citem['31'] = jdSj
            citem['32'] = jgSj
            citem['33'] = tdLy
            citem['34'] = tdSyqr
            citem['35'] = dzBaBh
            citem['36'] = zfSj
            citem['37'] = zfJe

            print(citem)

            if zdzl is None:
                raise ValueError('内容访问失败')
            else:
                """数据入库"""
                pymysql_connection().insert_into_doc(fields=citem, uuid=uuid)

        else:
            raise ValueError('内容访问失败')

    def msg(self, n, n1, n2, n3=''):
        n1 = str(n1) if n1 else None
        n2 = str(n2) if n2 else None
        obj1 = '≤' + n1 + n3 if n1 else ''
        obj2 = n2 + n3 + '≤' if n2 else ''
        obj1 = obj1.replace('≤', '') if '--' in obj1 else obj1
        obj2 = obj2.replace('≤', '') if '--' in obj2 else obj2
        obj = obj2 + f' {n} ' + obj1
        return obj


if __name__ == '__main__':
    s = Spider().start_request()
