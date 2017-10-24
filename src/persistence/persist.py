# from redis import StrictRedis
import redis_sentinel_url
from src.settings import REDIS_URL_CONNECTION, REDIS_KEY_TTL


class Persistence(object):

    def __init__(self):
        # self.client = StrictRedis.from_url(REDIS_URL_CONNECTION)
        self.sentinel, self.client = redis_sentinel_url.connect('redis+{}'.format(REDIS_URL_CONNECTION))
        self.ttl_seconds = REDIS_KEY_TTL

    def was_notified(self, task):
        return self.client.exists(task.id)

    def set_notified(self, task):
        self.client.set(task.id, task.__dict__, self.ttl_seconds)
