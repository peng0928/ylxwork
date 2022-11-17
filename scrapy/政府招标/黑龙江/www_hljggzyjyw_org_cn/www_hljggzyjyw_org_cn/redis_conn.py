import redis


class redis_conn():
    def __init__(self):
        redis_pool = redis.ConnectionPool(host='172.17.199.146', port=6379, db=8)
        self.redis_conn = redis.Redis(connection_pool=redis_pool)

    ##########断点续爬###########
    def set_add(self, field=None, value=None):
        self.redis_conn.sadd(field, value)
        print(f'sadd success value={value}')

    def get_data(self, field=None):
        result = self.redis_conn.smembers(field)
        return result

    def del_data(self, field=None, value=None):
        self.redis_conn.srem(field, value)
        print(f'del success value={value}')

    def find_data(self, field='bidding', value=None):
        result = self.redis_conn.sismember(field, value)
        return result


if __name__ == '__main__':
    r = redis_conn()
    s = r.find_data(value='http://a.xjbt.gov.cn/TPFront/infodetail/?infoid=b543edb3-7ebc-41bb-8610-23dced1c0c75&CategoryNum=004001002')
    print(s)