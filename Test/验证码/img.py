# -*- coding: utf-8 -*-
# @Date    : 2022-09-09 13:53
# @Author  : chenxuepeng
import ddddocr, requests, time, wget, os, base64
from PIL import Image, ImageEnhance, ImageFilter


def get_code(url=None, data=None, headers=None, methon='GET'):
    name = int(time.time())
    Name = f'./file/{name}.jpg'
    if methon == 'POST':
        url = 'http://ggzy.hebei.gov.cn/EWB-FRONT/rest/frontAppNotNeedLoginAction/getVerificationCode'
        data = 'params=%7B%22width%22%3A%22100%22%2C%22height%22%3A%2240%22%2C%22codeNum%22%3A%224%22%2C%22interferenceLine%22%3A%221%22%2C%22codeGuid%22%3A%22%22%7D'
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Authorization": "Bearer bdc2ae5a5fa64a55687a2ab1f344025d",
            "Connection": "keep-alive",
            "Content-Length": "158",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "JSESSIONID=5EC3E249A930BF65FCC5195451BC9CF1; _CSRFCOOKIE=B2E97D0E2AD3938C65CB97472888CF6DB6D46A09; EPTOKEN=B2E97D0E2AD3938C65CB97472888CF6DB6D46A09; _gscu_1921552764=65370490miuqjh11; oauthClientId=demoClient; oauthPath=http://172.19.3.38:8080/EpointWebBuilderZw; oauthLoginUrl=http://172.19.3.38:8080/EpointWebBuilderZw/rest/oauth2/authorize?client_id=demoClient&state=a&response_type=code&scope=user&redirect_uri=; oauthLogoutUrl=http://172.19.3.38:8080/EpointWebBuilderZw/rest/oauth2/logout?redirect_uri=; noOauthRefreshToken=82540504f9b2391f43cbce30a279101a; noOauthAccessToken=bdc2ae5a5fa64a55687a2ab1f344025d; _gscbrs_1921552764=1; _gscs_1921552764=667454118bcdjq21|pv:3",
            "Host": "ggzy.hebei.gov.cn",
            "Origin": "http://ggzy.hebei.gov.cn",
            "Referer": "http://ggzy.hebei.gov.cn/hbggfwpt/jydt/salesPlat.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        response = requests.post(url=url, data=data, headers=headers)
        imgcode = response.json()['custom']['imgCode']
        verificationcodeguid = response.json()['custom']['verificationCodeGuid']
        download_code(imgcode, name, base=True)

        code = docr(Name)

        # os.remove(Name)
        print(code)
        return code, verificationcodeguid

    else:
        download_code(url=url, name=name)
        code = docr(Name)
        print(code)


def download_code(url, name, base=False):
    if base:
        h, code = url.strip().split(',')
        img = base64.urlsafe_b64decode(code)
    else:
        img = requests.get(url).content
    with open(f'./file/{name}.jpg', 'wb')as f:
        f.write(img)


def docr(imgpath):
    ocr = ddddocr.DdddOcr(show_ad=False)
    img = Image.open(imgpath)
    res = ocr.classification(img)
    return res

false_i = 0
success_i = 0

def test_code():
    global success_i, false_i
    getcode = get_code(methon='POST')
    ImgGuid = getcode[1]
    YZM = getcode[0]
    url = 'http://ggzy.hebei.gov.cn/EWB-FRONT/rest/GgSearchAction/getInfoMationListyzm'
    data = f'siteGuid=7eb5f7f1-9041-43ad-8e13-8fcb82ea831a&categoryNum=003001001&keyword=&pageIndex=50&pageSize=10&code=&YZM={YZM}&ImgGuid={ImgGuid}&txtname=&starttime=&endtime='
    headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Authorization": "Bearer bdc2ae5a5fa64a55687a2ab1f344025d",
    "Connection": "keep-alive",
    "Content-Length": "158",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "JSESSIONID=5EC3E249A930BF65FCC5195451BC9CF1; _CSRFCOOKIE=B2E97D0E2AD3938C65CB97472888CF6DB6D46A09; EPTOKEN=B2E97D0E2AD3938C65CB97472888CF6DB6D46A09; _gscu_1921552764=65370490miuqjh11; oauthClientId=demoClient; oauthPath=http://172.19.3.38:8080/EpointWebBuilderZw; oauthLoginUrl=http://172.19.3.38:8080/EpointWebBuilderZw/rest/oauth2/authorize?client_id=demoClient&state=a&response_type=code&scope=user&redirect_uri=; oauthLogoutUrl=http://172.19.3.38:8080/EpointWebBuilderZw/rest/oauth2/logout?redirect_uri=; noOauthRefreshToken=82540504f9b2391f43cbce30a279101a; noOauthAccessToken=bdc2ae5a5fa64a55687a2ab1f344025d; _gscbrs_1921552764=1; _gscs_1921552764=667454118bcdjq21|pv:3",
    "Host": "ggzy.hebei.gov.cn",
    "Origin": "http://ggzy.hebei.gov.cn",
    "Referer": "http://ggzy.hebei.gov.cn/hbggfwpt/jydt/salesPlat.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
    response = requests.post(url=url, data=data, headers=headers)
    response.encoding = 'utf-8'

    message = response.json()
    print(message, response.status_code )
    if message.get('custom', False):
        false_i += 1
    else:
        success_i += 1

    print('success:', success_i, 'false:', false_i, 'all:', str(float(success_i/(success_i+false_i))*100) + '%')


def test_code2():
    url = 'http://ggzy.hebei.gov.cn/inteligentsearchfw/rest/inteligentSearch/getFullTextData'
    data = 'siteGuid=7eb5f7f1-9041-43ad-8e13-8fcb82ea831a&categoryNum=003001001&keyword=&pageIndex=52&pageSize=10&code=&YZM=52jd&ImgGuid=87cefa5a-1f5e-4da5-b086-19f8e55b003b&txtname=&starttime=&endtime='
    headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
    response = requests.post(url=url, data=data, headers=headers)
    print(response.status_code)

def tes():
    import easyocr
    reader = easyocr.Reader(['ch_sim', 'en'])
    result = reader.readtext('./file/1663744051.jpg')

    print(result)

if __name__ == '__main__':
    for i in range(1000):
        try:
            test_code()
        except Exception as e:
            print(e)