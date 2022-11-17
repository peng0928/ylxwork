from .pymysql_connection import pymysql_connection


class Pipeline:
    def process_item(self, item, spider):
        table = 'bidding_day_data_snapshots'
        db = pymysql_connection()

        db.insert_into_doc(fields=item, redis_field='政府招标:山东:www.ccgp-shandong.gov.cn', redis_value=item['pageurl'],tablename=table)
        return item