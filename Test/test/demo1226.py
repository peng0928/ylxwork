import requests, uuid
from lxml import etree
import urllib
from urllib import parse

uuid_list = []

def get_VIEWSTATE(next=False, Cookie=None, data=None):
    url = 'http://183.66.171.75:88/CQCollect/Qy_Query/Zjzxjg/Zjzxjg_List.aspx'
    if next:
        h2 = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": Cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        res2 = requests.post(url=url, data=data, headers=h2)
        tree2 = etree.HTML(res2.text)
        name = tree2.xpath("//td[@class='td_Main']/table[@id='DataGrid1']//tr/td[2]//text()")
        VIEWSTATE = tree2.xpath("//input[@name='__VIEWSTATE']/@value")
        VIEWSTATE = urllib.parse.quote(VIEWSTATE[0], 'utf-8') if VIEWSTATE else VIEWSTATE
        data = f'__EVENTTARGET=Pager1%3ALB_Next&__EVENTARGUMENT=&__VIEWSTATE={VIEWSTATE}&txt_EnpName=&Pager1%3ANewPage='
        uuidname = uuid.uuid5(uuid.NAMESPACE_DNS, str(name)).hex
        if uuidname in uuid_list:
            print('退出')
        else:
            print(name)
            uuid_list.append(uuidname)
            get_VIEWSTATE(data=data, next=True, Cookie=Cookie)
    else:
        h = {
        "Cookie": Cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        res = requests.get(url=url, headers=h)
        tree = etree.HTML(res.text)
        VIEWSTATE = tree.xpath("//input[@name='__VIEWSTATE']/@value")
        VIEWSTATE = urllib.parse.quote(VIEWSTATE[0], 'utf-8') if VIEWSTATE else VIEWSTATE
        data = f'__EVENTTARGET=Pager1%3ALB_Next&__EVENTARGUMENT=&__VIEWSTATE={VIEWSTATE}&txt_EnpName=&Pager1%3ANewPage='
        name = tree.xpath("//td[@class='td_Main']/table[@id='DataGrid1']//tr/td[2]//text()")
        print(name)
        uuidname = uuid.uuid5(uuid.NAMESPACE_DNS, str(name)).hex
        if uuidname in uuid_list:
            print('退出')
        else:
            uuid_list.append(uuidname)
            get_VIEWSTATE(data=data, next=True, Cookie=Cookie)

def get_data():
    url = 'http://183.66.171.75:88/CQCollect/Qy_Query/Zjzxjg/Zjzxjg_Info.aspx?type=0&CheckID=B2CEE9A3-00CA-4D94-BB91-DB7A75440E6C'
    headers = {
"Cookie": "ASP.NET_SessionId=fitzf1qfkpeve0j23qwpnf55",
"Pragma": "no-cache",
"Referer": "http: //183.66.171.75: 88/CQCollect/Qy_Query/Zjzxjg/Zjzxjg_List.aspx",
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}
    res = requests.get(url, headers=headers)
    tree = etree.HTML(res.text)
    querydict = tree.xpath("//div[@id='MyDiv']/table//tr/td/table//tr")
    textlist = []
    textdict = {}
    for query in querydict:
        cqueryset = query.xpath('./td')
        for quert in cqueryset:
            text = quert.xpath('.//text()')
            text = ''.join(text).replace('\r', '').replace('\t', '').replace('\n', '').replace('\xa0', '')
            textlist.append(text)
    for query in range(0, len(textlist), 2):
        textdict[textlist[query]] = textlist[query+1]
    print(textdict)

get_data()
