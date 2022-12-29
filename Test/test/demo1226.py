import requests, uuid
from lxml import etree
import urllib
from urllib import parse

uuid_list = []

def get_VIEWSTATE(next=False, Cookie=None, data=None):
    url = 'http://183.66.171.75:88/CQCollect/Qy_Query/Jlqy/Jlqy_List.aspx'
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
        data = f'__EVENTTARGET=TurnPage1%3ALB_Next&__EVENTARGUMENT=&__VIEWSTATE={VIEWSTATE}&txt_EnpName=&TurnPage1%3APageNum='
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
        data = f'__EVENTTARGET=TurnPage1%3ALB_Next&__EVENTARGUMENT=&__VIEWSTATE={VIEWSTATE}&txt_EnpName=&TurnPage1%3APageNum='
        name = tree.xpath("//td[@class='td_Main']/table[@id='DataGrid1']//tr/td[2]//text()")
        print(name)
        uuidname = uuid.uuid5(uuid.NAMESPACE_DNS, str(name)).hex
        if uuidname in uuid_list:
            print('退出')
        else:
            uuid_list.append(uuidname)
            get_VIEWSTATE(data=data, next=True, Cookie=Cookie)

get_VIEWSTATE(Cookie='ASP.NET_SessionId=a3xckqzncbx21r41d0walbj2')
