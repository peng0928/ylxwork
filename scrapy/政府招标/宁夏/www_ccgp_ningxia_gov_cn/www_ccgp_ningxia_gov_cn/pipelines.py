from itemadapter import ItemAdapter
from .pymysql_connection import pymysql_connection
from .settings import *

class Pipeline:
    def process_item(self, item, spider):
        fields = {}
        table = 'bidding_day_data_snapshots'
        db = pymysql_connection()
        for k, v in item.items():
            fields[k] = v

        # redis_field = redis_name
        db.insert_into_doc(fields=fields, tablename=table)
        return item