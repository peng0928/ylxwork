from itemadapter import ItemAdapter
from .pymysql_connection import pymysql_connection
from .settings import *

class Pipeline:
    def process_item(self, item, spider):
        db = pymysql_connection()
        db.insert_into_doc(fields=item)
        return item