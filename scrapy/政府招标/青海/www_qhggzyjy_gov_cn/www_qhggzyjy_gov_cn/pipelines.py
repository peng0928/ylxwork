from itemadapter import ItemAdapter
from .pymysql_connection import pymysql_connection
from www_qhggzyjy_gov_cn.settings import *

class Pipeline:
    def process_item(self, item, spider):
        fields = {}
        table = 'bidding_day_data_snapshots'
        redis_value = item['pageurl'] + '|' + item['publishdate']+ '|' + item['docsubtitle']
        db = pymysql_connection()
        for k, v in item.items():
            fields[k] = v

        redis_field = redis_name
        db.insert_into_doc(fields=fields, tablename=table, redis_field=redis_field, redis_value=redis_value)
        return item