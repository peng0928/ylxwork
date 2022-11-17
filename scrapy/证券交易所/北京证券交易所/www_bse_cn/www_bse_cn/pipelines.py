from .pymysql_connection import pymysql_connection


class Pipeline:
    def process_item(self, item, spider):
        table = 'listed_company_pdf'
        db = pymysql_connection()
        db.insert_into_doc(fields=item, tablename=table)
        return item