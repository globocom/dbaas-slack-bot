from unittest import TestCase
from unittest.mock import patch
from src.persistence.persist import Persistence
from src.settings import REDIS_KEY_TTL, REDIS_URL_CONNECTION
from tests import build_task_database, build_task_running


class FakeCache():
    def __init__(self):
        self.cached = {}

    def set(self, key, value, *args):
        self.cached[key] = value

    def exists(self, key):
        return key in self.cached


class TestPersist(TestCase):

    @patch('src.persistence.persist.StrictRedis.from_url')
    def test_connection(self, redis_from_url):
        persistence = Persistence()
        self.assertIsNotNone(persistence.client)
        redis_from_url.assert_called_once_with(REDIS_URL_CONNECTION)
        self.assertEqual(persistence.ttl_seconds, REDIS_KEY_TTL)

    def test_notified(self):
        persistence = Persistence()
        persistence.client = FakeCache()

        task_db = build_task_database()
        task_running = build_task_running()
        persistence.set_notified(task_running)

        self.assertFalse(persistence.was_notified(task_db))
        self.assertTrue(persistence.was_notified(task_running))
