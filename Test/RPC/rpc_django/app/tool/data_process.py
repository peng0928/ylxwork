import re, time, requests, json, datetime
from dateutil.relativedelta import relativedelta
from lxml import etree
from fake_useragent import UserAgent
from urllib.parse import urljoin


class Xpath():
    def __init__(self, response, encoding='utf-8'):
        if isinstance(response, str):
            self.res = etree.HTML(response)
        else:
            response.encoding = encoding
            self.res = etree.HTML(response.text)

    def xpath(self, x=None, filter='style|script', character=True, is_list=False, easy=False):
        if filter != None:
            tree = xpath_filter(self.res, filter=filter)
            x = x.split('|')
            if easy:
                x = [i + '/text()' if '/@' not in i else i for i in x]
            else:
                x = [i + '//text()' if '/@' not in i else i for i in x]
            x = '|'.join(x)

            obj = tree.xpath(x)
            obj = process_text(obj, character, is_list)

        else:
            x = x.split('|')
            if easy:
                x = [i + '/text()' if '/@' not in i else i for i in x]
            else:
                x = [i + '//text()' if '/@' not in i else i for i in x]
            x = '|'.join(x)
            obj = self.res.xpath(x)
            obj = process_text(obj, character, is_list)

        return obj

    def dpath(self, x=None, rule=None):
        x = x.split('|')
        x = [i + '//text()' if '/@' not in i else i for i in x]
        x = '|'.join(x)

        obj = self.res.xpath(x)
        obj = ' '.join(obj)
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
                        re.search(r'(\.tar|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)',
                                  str(filename[i])))
                    is_link = bool(
                        re.search(r'(\.tar|\.zip|\.pdf|\.png|\.doc|\.txt|\.ppt|\.html|\.xls|\.rar|\.jpg)',
                                  str(filelink[i])))
                    if is_file or is_link:
                        fn.append(filename[i])
                        fk.append(filelink[i])
                    else:
                        pass
                if fn is not None and fk is not None:
                    filename = '|'.join(fn)
                    filename = replace(filename).replace('\n', '')
                    filelink = [urljoin(rule, i) for i in fk]
                    filelink = '|'.join(filelink)

                if len(filelink) == 0 or len(filename) == 0:
                    return None, None
                else:
                    return filename, filelink
            else:
                return None, None
        except:
            return None, None


# 取出时间 data->时间戳，文本
def process_date(data=None, rule=None):
    data = data.replace('年', '-').replace('月', '-').replace('日', ' ').replace('/', '-').replace('.', '-')
    if len(data) == 0:
        return None

    if len(data) == 13 and '-' not in data:
        localtime = time.localtime(int(data) / 1000)
        date = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        return date

    if len(data) == 10 and '-' not in data:
        localtime = time.localtime(int(data))
        date = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        return date

    else:
        if rule != None:
            patten = '[' + rule + r']*(\d{1,4}-\d{1,2}-\d{1,2})'
            result = re.findall(patten, data)
        else:
            patten = r'(\d{1,4}-\d{1,2}-\d{1,2})'
            result = re.findall(patten, data)

        if len(result) == 0:
            return None
        else:
            result = re.findall('\d{4}-\d{1,2}-\d{1,2}', result[0])[0]
            return timechange(result)


# 中文数据转阿拉伯数字
def cnnum2albnum(s):
    # 二十
    if len(s) == 2:
        s = s.replace("二十", "20").replace("三十", "20")
    else:
        s = s.replace("二十", "2").replace("三十", "3")

    # 十
    if len(s) == 1:
        s = s.replace("十", "10")
    else:
        s = s.replace("十", "1")

    s = s.replace("○", "0")
    s = s.replace("〇", "0")
    s = s.replace("零", "0")
    s = s.replace("一", "1")
    s = s.replace("二", "2")
    s = s.replace("三", "3")
    s = s.replace("叁", "3")
    s = s.replace("四", "4")
    s = s.replace("五", "5")
    s = s.replace("伍", "5")
    s = s.replace("六", "6")
    s = s.replace("陆", "6")
    s = s.replace("七", "7")
    s = s.replace("八", "8")
    s = s.replace("九", "9")
    s = s.replace("拾", "0")
    s = s.replace("万", "0000")
    s = s.replace("千", "000")
    s = s.replace('年', '-').replace('月', '-').replace('日', '').replace('/', '-').strip()
    return s


def numreplace(s):
    if s != '10':
        s = s.replace("0", "零")
        s = s.replace("1", "一")
        s = s.replace("2", "二")
        s = s.replace("3", "三")
        s = s.replace("4", "四")
        s = s.replace("5", "五")
        s = s.replace("6", "六")
        s = s.replace("7", "七")
        s = s.replace("8", "八")
        s = s.replace("9", "九")
    else:
        s = s.replace("10", "拾")
    return s


def numtohans(s):
    fresult = re.findall('\d+', s)
    if fresult is None or len(fresult) == 0:
        return s
    else:
        lfresult = len(fresult[0])
        s = numreplace(s)
        if lfresult == 2 and s != '拾':
            s = s[0] + '十' + s[1:]
        if lfresult == 3:
            s = s[0] + '百' + s[1] + '十' + s[2:]
        return s


chinese_num = {
    u'〇': 0, u'零': 0,
    u'一': 1, u'壹': 1,
    u'二': 2, u'两': 2, u'贰': 2,
    u'三': 3, u'叁': 3,
    u'四': 4, u'肆': 4,
    u'五': 5, u'伍': 5,
    u'六': 6, u'陆': 6,
    u'七': 7, u'柒': 7,
    u'八': 8, u'捌': 8,
    u'九': 9, u'玖': 9,
    u'十': 10, u'拾': 10,
    u'百': 100, u'佰': 100,
    u'千': 1000, u'仟': 1000,
    u'万': 10000, u'萬': 10000,
    u'亿': 100000000, u'億': 100000000,
}


def chinese2digits(value):
    total = 0.00
    # 基础单位
    base_unit = 1
    # 可变单位
    dynamic_unit = 1
    for i in range(len(value) - 1, -1, -1):
        val = chinese_num.get(value[i])
        # 表示单位
        if val > 10:
            if val > base_unit:
                base_unit = val
            else:
                dynamic_unit = base_unit * val
        # 10既可以做单位也可做数字
        elif val == 10:
            if i == 0:
                if dynamic_unit > base_unit:
                    total = total + dynamic_unit * val
                else:
                    total = total + base_unit * val
            else:
                dynamic_unit = base_unit * val
        else:
            if dynamic_unit > base_unit:
                total = total + dynamic_unit * val
            else:
                total = total + base_unit * val
    return total


##时间戳->时间
def process_timestamp(t=None):
    if len(str(t)) != 10:
        t = str(t)[:10]
    else:
        t = t
    timeArray = time.localtime(int(t))
    formatTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return formatTime


##时间->时间戳
def timestamp(t=None, rule="%Y-%m-%d"):
    s_t = time.strptime(t, rule)
    mkt = int(time.mktime(s_t))
    return (mkt)


# 判断是否包含数字
def include_number(s):
    return bool(re.search(r'\d', str(s)))


# etree解析
def process_text(obj, character=True, is_list=False):
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
    if is_list:
        return L

    if character:
        result = '\n'.join(L)
        result = replace(result)
    else:
        result = ''.join(L)
        result = replace(result)
    if len(result) == 0:
        return None
    else:
        return result.replace("'", "‘").replace('"', '“').strip()


def replace(str):
    result = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"), str)
    result = re.sub(r'(\\r|\\n|\\t|\xa0)', lambda x: '', result)
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


def get_datetime_now(rule='%Y-%m-%d', reduce_year=0, reduce_months=0):
    daytime = datetime.datetime.now()
    if reduce_year or reduce_months:
        daytime = ((daytime - relativedelta(years=reduce_year, months=reduce_months)).strftime(rule))
    else:
        daytime = daytime.strftime(rule)
    return daytime


# 微秒级时间戳
def microsecond_timestamp():
    t = time.time()
    docIdTime = int(round(t * 1000000))
    return docIdTime


# md5
def encrypt_md5(key=None):
    import hashlib
    key = bytes(key, 'utf-8')
    m = hashlib.md5()
    m.update(key)
    result = m.hexdigest()
    return result


# 获取工作日时间
def weekday_1(start_date=None, Y=False, M=False, D=False):
    import pandas as pd
    from datetime import datetime
    e = pd.bdate_range(start_date, datetime.now().strftime('%Y-%m-%d'), freq='b')
    if Y is True:
        e = [i.strftime('%Y') for i in e]
    elif M is True:
        e = [i.strftime('%m') for i in e]
    elif D is True:
        e = [i.strftime('%d') for i in e]
    else:
        e = [i.strftime('%Y-%m-%d') for i in e]
    e.reverse()
    return e


def timechange(start_date):
    middle = datetime.datetime.strptime(start_date.replace('/', '-'), '%Y-%m-%d')
    end_date = datetime.datetime.strftime(middle, '%Y-%m-%d')
    return end_date


def url_join(baseurl, url):
    if isinstance(url, list):
        for i in range(len(url)):
            if re.findall('^http', url[i]):
                pass
            else:
                url[i] = urljoin(baseurl, url[i])

    if isinstance(url, str):
        if re.findall('^http', url):
            pass
        else:
            url = urljoin(baseurl, url)
    return url


def error(e):
    datenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = {
        '时间': datenow,
        '错误信息': e,
    }
    return msg


def trycatch(t=None):
    '''
    :param t: 重试次数
    :param retry_num: 初始重试次数
    :return:
    '''

    def wrap(x):

        def inner(*args, **kwargs):
            retry_num = 0
            try:
                return x(*args, **kwargs)
            except Exception as e:
                msg = error(e)
                print(msg, t)

                while True:
                    retry_num += 1
                    if retry_num > t:
                        return '超出重试次数!'
                    try:
                        print('正在尝试重试:', retry_num)
                        return x(*args, **kwargs)
                    except Exception as e:
                        msg = error(e)
                        print(msg, t)

        return inner

    return wrap