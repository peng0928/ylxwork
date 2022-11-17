# -*- coding: utf-8 -*-
# @Date    : 2022-10-10 15:41
# @Author  : chenxuepeng
import re
s = '[7]1asas'

l = re.sub('(\[\d\])', 'abc', s)
print(l)