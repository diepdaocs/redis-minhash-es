from abc import ABC, abstractmethod

from redis import StrictRedis


class KVStorage(ABC):

    @abstractmethod
    def put(self, name, key, value):
        pass

    @abstractmethod
    def get(self, name, key):
        pass

    @abstractmethod
    def delete(self, key):
        pass


class RedisStorage(KVStorage):
    def __init__(self, host='localhost', port=6379):
        self.redis_client = StrictRedis(host, port, decode_responses=True)

    def put(self, name, key, value):
        self.redis_client.hset(name, key, value)

    def get(self, name, key):
        value = self.redis_client.hget(name, key)
        if value == 'None':
            return None

        return value

    def delete(self, key):
        self.redis_client.delete(key)
