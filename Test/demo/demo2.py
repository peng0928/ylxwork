import requests, re, copy
from lxml import etree

# response = requests.get(url='http://ky.mnr.gov.cn/gs_174/tkqzrgsxm/201308/t20130827_2468031.htm')
response = requests.get(url='http://ky.mnr.gov.cn/gs_174/tkqgsxm/202211/t20221112_8396580.htm')
response.encoding = 'utf-8'
tree = etree.HTML(response.text)
table_filter = ['交易', '结果', '信息']
table_key = [
    '转让金额（万元）',
    '成交价（万元）',
    '出让方式',
    '竞得人（中标人）',
    '转让方',
    '名称',
    '法定代表人',
    '竞得人公司地址',
    '成交地点',
    '价款缴纳方式',
    '价款缴纳时间',
    '成交时间',
    '项目名称',
    '地址',
    '矿种',
    '面积（km²）',
    '发证机关',
    '有效期起',
    '许可证号',
    '有效期止',
    '地理位置',
    '出让年限（年）',
    '转让方式',
    '区域坐标',
    '受让方',
]

table_dict = {}
table_list = []
table_tr = tree.xpath("//body[@class='line_height']/table//tr[2]/td/table//tr")
for item in table_tr:
    table_td = item.xpath('./td//text()')
    level = 0
    le = False
    table_level1 = []
    table_level2 = []
    table_level3 = []
    table_value = []
    for query in table_td:
        query = query.replace(' ', '')
        query2 = query.replace(' ', '').replace('\xa0', '').replace('\n', '')
        if query2 in table_filter or query == '\n':
            continue
        query = query.replace('\xa0', '').replace('\n', '')
        if query == '区域坐标':
            cdata = item.xpath("./td[2]//text()")
            arealist = []
            for i in cdata:
                i = i.replace('\n', '').replace(' ', '').replace('\r', '').replace('\t', '')
                if i != '':
                    arealist.append(i)
            area = re.findall("varvalue='(.*?)';var", arealist[-1])[0].split(',')

            area = [i for i in area[:-2] if i != '']
            # fnum = int(area[1])
            area = area[2:]
            area = [i for i in area if '.' in i]
            ar = 0
            ar_list2 = []
            lle = len(arealist[:-1]) - 2 if '拐点' in arealist else len(arealist[:-1]) - 1
            try:
                for i in range(0, len(area), lle):
                    xx = copy.deepcopy(arealist[1:-1])
                    areadict = {}
                    ar += 1
                    arr = 0
                    areadict['序号'] = ar
                    if '拐点' in xx:
                        areadict['拐点'] = ar
                        xx.remove('拐点')
                    else:
                        pass

                    for _ in xx:
                        areadict[_] = area[i + arr]
                        arr += 1
                    ar_list2.append(areadict)
            except:
                pass
            table_dict['区域坐标'] = ar_list2
            break

        if query in table_key:
            level += 1
            if level == 2:
                table_level2.append(query)
            else:
                if query not in table_list:
                    table_list.append(query)
                    table_level1.append(query)
                else:
                    table_list.append(query + '1')
                    table_level1.append(query + '1')
        else:
            level -= 1
            table_value.append(query)

    level2 = []
    if table_level2:
        for i in range(len(table_level2)):
            dic = {table_level2[i]: table_value[i]}
            level2.append(dic)
        table_dict[table_level1[0]] = level2
    else:
        for i in range(len(table_level1)):
            table_dict[table_level1[i]] = table_value[i]

print(table_dict)
