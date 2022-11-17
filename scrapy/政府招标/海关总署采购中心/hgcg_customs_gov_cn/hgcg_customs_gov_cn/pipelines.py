from itemadapter import ItemAdapter
from hgcg_customs_gov_cn.pymysql_connection import pymysql_connection
from hgcg_customs_gov_cn.settings import *

class Pipeline:
    def process_item(self, item, spider):
        table = 'bidding_day_data_snapshots'
        db = pymysql_connection()
        db.insert_into_doc(fields=item, tablename=table)
        return item