from itemadapter import ItemAdapter
from www_ggzyzx_jl_gov_cn.pymysql_connection import pymysql_connection
from www_ggzyzx_jl_gov_cn.settings import *

class Pipeline:
    def process_item(self, item, spider):
        fields = {}
        table = 'bidding_day_data_snapshots'
        db = pymysql_connection()
        for k, v in item.items():
            fields[k] = v


        db.insert_into_doc(fields=fields, tablename=table)
        return item