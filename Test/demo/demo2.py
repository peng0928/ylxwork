import requests, re
from lxml import etree

url = 'http://ky.mnr.gov.cn/gs_174/ckqgsxm/202211/t20221130_8412178.htm'

response = requests.get(url)
response.encoding = 'utf-8'
tree = etree.HTML(response.text)

contents = tree.xpath("//body[@class='line_height']/table//tr[2]/td/table//tr")


def get_c(contents):
    cdict = {}
    condition = False
    for citem in contents:
        key = []
        value = []
        qqq = []
        titem = citem.xpath('./td')
        i = 0
        for item in titem:
            if condition is False:
                i += 1
                cdata = item.xpath(".//text()")
                cdata = ''.join(cdata).replace('\xa0', '').replace('\n', '').replace(' ', '') if cdata else cdata
                if cdata == '区域坐标':
                    cdata = citem.xpath("./td[2]//text()")
                    arealist = []
                    for i in cdata:
                        i = i.replace('\n', '').replace(' ', '').replace('\r', '').replace('\t', '')
                        if i != '':
                            arealist.append(i)

                    area = re.findall("varvalue='(.*?)';var", arealist[-1])[0].split(',')
                    area = [i for i in area[:-2] if i != '']
                    fnum = int(area[1])
                    area = area[2:]
                    ar = 0
                    ar_list2 = []
                    try:
                        for i in range(0, len(area), len(arealist[:-1]) - 1):
                            areadict = {}
                            ar += 1
                            arr = 0
                            areadict['序号'] = ar
                            for _ in arealist[1:-1]:
                                areadict[_] = area[i + arr]
                                arr += 1
                            ar_list2.append(areadict)
                    except:
                        pass
                        # print(areadict)
                    key.append('区域坐标')
                    value.append(ar_list2)
                    condition = True

                else:
                    if cdata:
                        qqq.append(cdata)

        for i in range(0, len(qqq), 2):
            if qqq[0] == '交易结果信息':
                try:
                    # print(qqq[i+1], )
                    key.append(qqq[i+1])
                    value.append(qqq[i + 2])
                except:
                    pass
            else:
                try:
                    key.append(qqq[i])
                    value.append(qqq[i+1])
                except:
                    key.append(qqq[i])
                    value.append('')


        for l in range(len(key)):
            try:
                cdict[key[l]] = value[l]
            except:
                cdict[key[l]] = ''
    return cdict


print(get_c(contents))
