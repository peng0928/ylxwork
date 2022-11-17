# -*- coding: utf-8 -*-
# @Date    : 2022-10-08 16:27
# @Author  : chenxuepeng
import requests, re, json
from fake_useragent import UserAgent
from pymsql109 import *
from lxml import etree
from data_process import *


def unicode_escape(word=None):
    if isinstance(word, bytes):
        word = str(word, 'unicode_escape')
        word = bytes(word, 'unicode_escape')
        return word.decode('unicode_escape')
    if isinstance(word, str):
        word = re.sub(r'(\\u[a-zA-Z0-9]{4})', lambda x: x.group(1).encode("utf-8").decode("unicode-escape"), word)
        word = bytes(word, 'unicode_escape')
        return word.decode('unicode_escape')


class MainSpider():

    def __init__(self):
        p = pymysql_connection()
        self.leader_data = p.get_leader()

    def leader_spider(self):
        for item in self.leader_data[162:]:
            leader_list = []
            other_leader_list = []
            parse_result = 0
            id = item[0]
            provincial = item[1]
            prefecture = item[2]
            type = item[3]
            position = item[4]
            position = position.replace('/', '、').replace('，', '、').split('、')
            position = [re.sub('\((.*?)\)', '', i) if '(' in i else i for i in position]
            position = [re.sub('（(.*?)）', '', i) if '（' in i else i for i in position]
            leader_name = item[5]

            leader_name = re.findall('(.*?)\(', leader_name)[0] if '(' in leader_name else leader_name
            # if leader_name == '樊成华':
            url = f'https://baike.baidu.com/item/{leader_name}?force=1'
            headers = {'user-agent': UserAgent().random}
            response = requests.get(url=url, headers=headers)
            response.encoding = 'utf-8'

            print(url)
            # 判断是否存在多个重复名字
            tree = etree.HTML(response.text)
            is_exists = tree.xpath("//div[@class='lemmaWgt-subLemmaListTitle']")
            is_exists_list = []
            is_exists_list2 = []
            content_list = []
            is_exists_is = False
            try:
                # 搜索结果多个
                if is_exists:
                    cols = tree.xpath("//div[@class='para']/a")

                    # 判断省-一级
                    for item in cols:
                        name = item.xpath('./text()')[0]
                        link = item.xpath('./@href')[0]
                        if provincial in name:
                            is_exists_list.append(name + '^' + link)

                    # 省判断为空接着判断市-二级
                    if len(is_exists_list) == 0:
                        for item in cols:
                            name = item.xpath('./text()')[0]
                            link = item.xpath('./@href')[0]
                            if prefecture in name:
                                is_exists_list.append(name + '^' + link)

                    # 判断职位-三级
                    if len(is_exists_list) != 1:
                        for item2 in is_exists_list:
                            if prefecture in item2:
                                is_exists_list2.append(item2)
                        if len(is_exists_list2) != 1:
                            is_exists_list2 = []
                            for item3 in is_exists_list:
                                if is_exists_is is False:
                                    for i in position:
                                        if i in item3:
                                            is_exists_list2.append(item3)
                                            is_exists_is = True
                                            break
                                else:
                                    break

                        is_exists_list = copy.deepcopy(is_exists_list2)

                    if len(is_exists_list) == 1:
                        get_link = 'https://baike.baidu.com' + is_exists_list[0].split('^')[1]
                        print(get_link)
                        get_response = requests.get(url=get_link, headers=headers)
                        get_response.encoding = 'utf-8'

                        # 本词条缺少概述图，补充相关内容使词条更完整，还能快速升级，赶紧来编辑吧！
                        less_content = '<div class="edit-prompt">本词条缺少'
                        if less_content in get_response.text:
                            other_content_tree = etree.HTML(get_response.text)
                            other_contents = other_content_tree.xpath("//div[@class='lemma-summary']/div[@class='para']")
                            other_leader_list = self.other_parse(other_contents)

                            content_tree = etree.HTML(get_response.text)
                            contents = content_tree.xpath("//div[@class='para']")
                            leader_list = self.content_parse(contents)

                        # 人物履历
                        else:
                            other_content_tree = etree.HTML(get_response.text)
                            other_contents = other_content_tree.xpath(
                                "//div[@class='lemma-summary']/div[@class='para']")
                            other_leader_list = self.other_parse(other_contents)

                            content_source = re.findall(r'(</span>人物履历</h2>|</span>工作履历</h2>)(.*?)(</span>职务任免</h2>|</span>军衔晋升</h2>|</span>工作分工</h2>|</span>学习经历</h2>|</span>任免信息</h2>|</span>担任职务</h2>)',get_response.text, re.S)[0][1]
                            content_tree = etree.HTML(content_source)
                            contents = content_tree.xpath("//div[@class='para']")
                            leader_list = self.content_parse(contents)

                    if (len(leader_list)) == 0:
                        parse_result = 2
                        other_leader_list = ([None], [None], [None])
                    else:
                        parse_result = 1

                # 搜索结果单个
                else:
                    other_content_tree = etree.HTML(response.text)
                    other_contents = other_content_tree.xpath("//div[@class='lemma-summary']/div[@class='para']")
                    other_leader_list = self.other_parse(other_contents)


                    patten = r'(</span>人物履历</h2>|</span>工作履历</h2>)(.*?)(</span>职务任免</h2>|</span>工作分工</h2>|</span>分管工作</h2>|</span>任免信息</h2>|</span>担任职务</h2>|</span>社会兼职</h2>)'
                    content_source = re.findall(patten, response.text, re.S)[0][1]
                    content_tree = etree.HTML(content_source)
                    contents = content_tree.xpath("//div[@class='para']")
                    leader_list = self.content_parse(contents)
                    if (len(leader_list)) == 0:
                        parse_result = 2
                    else:
                        parse_result = 1

                if leader_list == []:
                    leader_list = None
                else:
                    leader_list = json.dumps(leader_list)
                    leader_list = unicode_escape(leader_list)
                    leader_list = escape_string(leader_list).replace(' ', '').strip()
            except:
                leader_list = None
                parse_result = 3
                other_leader_list = [None, None, None]

            education = other_leader_list[0]
            native_place = other_leader_list[1]
            birthday = other_leader_list[2]
            education = education[0] if education else None
            native_place = native_place[0] if native_place else None

            p = pymysql_connection()
            leader_list = 'null' if leader_list is None else leader_list
            birthday = None if not birthday else birthday[0]
            print('parse_result:', parse_result, native_place, education, birthday)
            p.update_leader(birthday=birthday, record=leader_list, parse_result=parse_result, id=id, education=education, native_place=native_place)

    '''
    :解析人物履历:
    '''
    def content_parse(self, contents):
        leader_list = []
        for content_item in contents:
            dic = {}
            content = content_item.xpath(".//text()")
            content = [i.replace('\n', '').replace('\xa0', '') for i in content]
            content = [re.sub('(\[\d+\])', '', i) for i in content]
            content = [re.sub('(\[\d+-\d+\])', '', i) for i in content]
            content = [i for i in content if i != '']
            content = ''.join(content).replace('－', '-')

            # 判断内容前四位为数字
            if bool(re.search(r'^\d{4}', str(content))):
                # 判断'—'是否存在-区分是否有时间段
                start_content = content.replace('—', '-').replace('--', '-')
                if '-' in start_content:
                    str_content = re.findall(
                        '(\d{4}\.\d{1,2}-\d{4}\.\d{1,2}|\d{4}年\d{1,2}月-\d{4}年\d{1,2}月|\d{4}-\d{4}年)(.*)', start_content)

                    # 样式：{'starttime': '2019-01', 'endtime': '2020-10', 'content': '北京市顺'}
                    if str_content:
                        last_content = str_content[0][1]
                        starttime = str_content[0][0].split('-')[0]
                        endtime = str_content[0][0].split('-')[1]
                    # 样式：{'starttime': '2019-01', 'endtime': '', 'content': '北京市顺'}
                    else:
                        str_content = re.findall('(\d{4}\.\d{1,2}-|\d{4}年\d{1,2}月-|\d{4}-)(.*)', start_content)
                        last_content = str_content[0][1]
                        starttime = str_content[0][0][:-1]
                        starttime = starttime[:-1] if starttime[-1] == '，' or starttime[-1] == '-' else starttime
                        endtime = ''

                    dic['starttime'] = starttime.replace('年', '-').replace('.', '-').replace('月', '')
                    dic['endtime'] = endtime.replace('年', '-').replace('.', '-').replace('月', '')
                    dic['endtime'] = dic['endtime'][:-1] if len(dic['endtime']) == 5 else dic['endtime']
                    dic['content'] = last_content[1:] if last_content[0] == '，' else last_content

                else:
                    # 样式：'starttime': '2021-09', 'endtime': '', 'content': '任北京市房山区委副书记'

                    if '月' in content or re.search('(\d{4}年\d{1,2}月|\d{4}\.\d{1,2})', content):
                        str_content = re.findall('(\d{4}年\d{1,2}月|\d{4}\.\d{1,2})(.*)', content)
                    else:
                        str_content = re.findall('(\d{4}年)(.*)', content)
                    starttime = str_content[0][0].replace('年', '-').replace('.', '-').replace('月', '')
                    starttime = starttime[:-1] if starttime[-1] == '，' or starttime[-1] == '-' else starttime
                    last_content = str_content[0][1]

                    dic['starttime'] = starttime
                    dic['endtime'] = ''
                    dic['content'] = last_content[1:] if last_content[0] == '，' else last_content

            else:
                dic['starttime'] = ''
                dic['endtime'] = ''
                dic['content'] = content

            leader_list.append(dic)
        return leader_list

    '''
    :解析学历、籍贯:
    '''
    def other_parse(self, contents):
        education_list, native_place_list, birthday = [], [], []
        for content_item in contents:
            content = content_item.xpath(".//text()")
            content = ''.join(content)

            '''出生年月'''
            birthdays = re.findall('(\d{4}年\d{1,2}月)(生|出生)', content)
            if birthdays:
                birthday.append(birthdays[0][0])

            if '毕业（' in content:
                education = re.findall('毕业（(.*?)）', content)
                education_list.append((education[0])) if education and '学士' not in education[0] else 'null'
            if len(education_list) == 0:
                education = re.findall('(.*?)毕业', content)
                education_list.append(self.other_replace(education[0])) if education else 'null'

            native_place = re.findall('(，|籍贯)(.*?)(人，)', content)
            native_place_list.append(self.other_replace(native_place[0][1])) if native_place else 'null'

        # print(education_list, native_place_list, birthday)
        return education_list, native_place_list, birthday

    '''
    :符号处理，用于分割:
    '''
    def other_replace(self, text):
        content = text.replace('年', '&').replace('月', '&').replace('，', '&').replace('。', '&').replace('？', '&').replace('；', '&').replace('！', '&')
        content = content.split('&')[-1]
        return content


if __name__ == '__main__':
    s = MainSpider()
    s.leader_spider()
