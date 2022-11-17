import redis


class redis_conn():
    def __init__(self, db=8):
        redis_pool = redis.ConnectionPool(host='10.0.2.248', port=6379, db=db)
        field = ''
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

    def find_data(self, field=None, value=None):
        result = self.redis_conn.sismember(field, value)
        return result

