import redis


class redis_conn():
    def __init__(self, db=1):
        redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=db)
        self.field = ''
        self.redis_conn = redis.Redis(connection_pool=redis_pool)

    def set_add(self, field=None, value=None):
        if field is None:
            field = self.field
        self.redis_conn.set(field, value)
        print(f'sadd success value={value}')

    def get_data(self, field=None):
        if field is None:
            field = self.field
        result = self.redis_conn.get(field)
        result = str(result, 'utf-8')
        return result

    def del_data(self, field=None, value=None):
        if field is None:
            field = self.field
        self.redis_conn.srem(field, value)
        print(f'del success value={value}')

    def find_data(self, field=None, value=None):
        if field is None:
            field = self.field
        result = self.redis_conn.sismember(field, value)
        return result

