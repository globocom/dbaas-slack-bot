# from redis import StrictRedis
from redis.sentinel import Sentinel
from src.settings import (REDIS_KEY_TTL, DBAAS_SENTINEL_ENDPOINT_SIMPLE,
                          DBAAS_SENTINEL_SERVICE_NAME, DBAAS_SENTINEL_PASSWORD)


class Persistence(object):

    def __init__(self):
        hosts_sentinel = DBAAS_SENTINEL_ENDPOINT_SIMPLE.replace("sentinel://", "")
        sentinels = list(map(lambda sentinel: tuple(sentinel.split(':')), hosts_sentinel.split(',')))
        sentinel = Sentinel(sentinels, socket_timeout=1)
        self.client = sentinel.master_for(DBAAS_SENTINEL_SERVICE_NAME, socket_timeout=1, password=DBAAS_SENTINEL_PASSWORD)
        self.ttl_seconds = REDIS_KEY_TTL

    def was_notified(self, task):
        return self.client.exists(task.id)

    def set_notified(self, task):
        self.client.set(task.id, task.__dict__, self.ttl_seconds)

    def set_channel(self, channel_id, relevance_id):
        self.client.set(relevance_id, channel_id)

    def unset_channel(self, relevance_id):
        self.client.delete(relevance_id)

    def channels_for(self, relevance):
        relevance_query = "{}_*".format(relevance)
        keys_list = self.client.keys(relevance_query)
        return [self.client.get(key) for key in keys_list]
      
