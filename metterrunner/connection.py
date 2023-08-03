import redis

pool = redis.ConnectionPool(host='192.168.1.33', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)
