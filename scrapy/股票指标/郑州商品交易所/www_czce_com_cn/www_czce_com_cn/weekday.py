# -*- coding: utf-8 -*-
# @Date    : 2022-08-30 13:45
# @Author  : chenxuepeng
import pandas as pd
from datetime import datetime

def weekday_1(start_date=None):
    e = pd.bdate_range(start_date, datetime.now().strftime('%Y-%m-%d'), freq='b')
    e = [i for i in e]
    e.reverse()
    return e


