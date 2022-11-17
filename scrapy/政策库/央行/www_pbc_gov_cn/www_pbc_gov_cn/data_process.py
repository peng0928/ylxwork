import re, time, requests, json, datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from fake_useragent import UserAgent


class Xpath():
    def __init__(self, response):
        self.res = etree.HTML(response)

    def xpath(self, x=None, filter=None):
        if filter != None:
            tree = xpath_filter(self.res, filter=filter)
            x = x.split('|')
            x = [i + '//text()' if '/@' not in i else i for i in x]
            x = '|'.join(x)

            obj = tree.xpath(x)
            obj = process_text(obj)

        else:
            x = x.split('|')
            x = [i + '//text()' if '/@' not in i else i for i in x]
            x = '|'.join(x)
            obj = self.res.xpath(x)
            obj = process_text(obj)

        return obj


    def dpath(self, x=None, p='', rule=None):
        le = x.split('|')
        if len(le) > 1:
            x = x.split('|')
            for item in x:
                p += item + '//text()|'
            x = p[:-1]
        else:
            x = x + '//text()'

        obj = self.res.xpath(x)
        obj = ''.join(obj)
        obj = process_date(data=obj, rule=rule)
        return obj


    def fxpath(self, x=None, p='', h='', rule=None):
        le = x.split('|')
        if len(le) > 1:
            x = x.split('|')
            for item in x:
                p += item + '//text()|'
                h += item + '//@href|'
            p = p[:-1]
            h = h[:-1]
        else:
            p = x + '//text()'
            h = x + '//@href'

        filename = self.res.xpath(p) or None
        filelink = self.res.xpath(h) or None
        fn = []
        fk = []
        try:
            if filename is not None and filelink is not None:
                for i in range(len(filelink)):
                    is_file = bool(
                        re.search(r'(\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar)', str(filename[i])))
                    is_link = bool(
                        re.search(r'(\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar)', str(filelink[i])))
                    if is_file or is_link:
                        fn.append(filename[i])
                        fk.append(filelink[i])
                    else:
                        pass
                if fn is not None and fk is not None:
                    if rule is None:
                        fileurl = ''
                    else:
                        fileurl = rule
                    filename = '|'.join(fn)
                    filelink = fileurl + f'|{fileurl}'.join(fk)
                return filename, filelink
            else:
                return None, None
        except Exception as e:
            print(e)


# 取出时间 data->时间戳，文本
def process_date(data=None, rule=None):
    data = data
    if len(data) == 0:
        return None
    if len(data) == 13:
        localtime = time.localtime(int(data) / 1000)
        date = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        return date

    if len(data) == 10 and '-' not in data:
        localtime = time.localtime(int(data))
        date = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        return date

    else:
        if rule != None:
            patten = '[' + rule + r']*(\d{1,4}[-|/|.|年]\d{1,2}[-|/|.|月]\d{1,2}[-|/|.|日]*)[\s]*([\d{1,2}]*[:|时]*[\d{1,2}]*[:分]*[\d{1,2}]*[秒]*)'
            result = re.findall(patten, data)
        else:
            patten = r'(\d{1,4}[-|/|.|年]\d{1,2}[-|/|.|月]\d{1,2}[-|/|.|日]*)[\s]*([\d{1,2}]*[:|时]*[\d{1,2}]*[:分]*[\d{1,2}]*[秒]*)'
            result = re.findall(patten, data)

        result = ' '.join(result[0]).replace('年', '-').replace('月', '-').replace('日', '').strip()
        return result


##时间戳
def process_timestamp(t=None):
    if len(str(t)) != 10:
        t = str(t)[:10]
    else:
        t = t
    timeArray = time.localtime(int(t))
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return formatTime


# 判断是否包含数字
def include_number(s):
    return bool(re.search(r'\d', str(s)))


# etree解析
def process_text(obj):
    L = []
    if isinstance(obj, str):
        L.append(obj)

    if isinstance(obj, list):
        for item in obj:
            if item.isspace():
                pass
            elif '\n' in item or '\t' in item:
                item = item.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')
                if len(item) == 0:
                    pass
                else:
                    L.append(item)
            else:
                L.append(item)

    result = '\n'.join(L).replace('?xml:namespace>', '') \
        .replace('\r', '').replace("'", '‘').replace(' ', '') \
        .replace('\xa0', '').replace('\u3000', '').replace('\u2002', '').replace("'", '’').replace("\t", '') \
        .replace('"', '”').replace('&nbsp', '').strip()

    if len(result) == 0:
        return None
    else:
        return result


def process_content_type(C=None, F=None):
    if C is None and F is None:
        return None
    if C is not None and F is not None:
        if len(C) != 0 and len(F) != 0:
            return 2
    if C is not None:
        if len(C) != 0:
            return 0
    if F is not None:
        if len(F) != 0:
            return 1


def xpath_filter(response=None, filter=None):
    filter_num = filter.split('|')
    if len(filter_num) > 1:
        filter = filter.split('|')
        filter = '//' + '|//'.join(filter)
    else:
        filter = '//' + filter

    # tree = etree.HTML(response)
    ele = response.xpath(filter)
    for e in ele:
        e.getparent().remove(e)
    return response


def get_link(url=None, headers=None, rpath=None):
    if headers is None:
        headers = {
            'user-agent': UserAgent().random}
    res = requests.get(url=url, headers=headers)
    res.encoding = 'utf-8'
    tree = etree.HTML(res.text)
    xpathobj = tree.xpath(rpath)
    return xpathobj


def get_link_json(url=None, headers=None, proxy=None):
    if headers is None:
        headers = {
            'user-agent': UserAgent().random,
            'Content-Type': 'application/json;charset=utf-8'}

    res = requests.get(url=url, headers=headers, proxies=proxy)
    res.encoding = 'utf-8'
    try:
        resjson = json.loads(res.text)
        return resjson
    except:
        return res.text


def post_link(url=None, rpath=None, data=None, headers=None):
    if headers is None:
        headers = {
            'user-agent': UserAgent().random}
    res = requests.post(url=url, data=data, headers=headers)
    res.encoding = 'utf-8'
    tree = etree.HTML(res.text)
    xpathobj = tree.xpath(rpath)
    return xpathobj


def post_link_json(url=None, data=None, headers=None, proxies=None):
    if headers is None:
        headers = {
            'user-agent': UserAgent().random,
            'Content-Type': 'application/json;charset=utf-8'}

    res = requests.post(url=url, data=data, headers=headers, proxies=proxies)
    if res.status_code == 200:
        res.encoding = 'utf-8'
        resjson = json.loads(res.text)
        return resjson
    else:
        return res.status_code, res.headers


def proxies():
    res = requests.get('http://127.0.0.1:5010/get/')
    proxy = res.json().get('proxy', None)
    proxies = {'http': proxy}
    return proxies


def req_proxies():
    proxies = {'http': 'tps163.kdlapi.com:15818'}
    return proxies


def get_datetime_now(rule='%Y-%m-%d', reduce=None):
    daytime = datetime.datetime.now()
    if reduce:
        daytime = ((daytime - relativedelta(years=reduce)).strftime(rule))
    else:
        daytime = daytime.strftime(rule)
    return daytime
