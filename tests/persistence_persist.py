from unittest import TestCase
from unittest.mock import patch
from src.persistence.persist import Persistence
from src.settings import REDIS_KEY_TTL
from tests import build_task_database, build_task_running


class FakeCache():
    def __init__(self):
        self.cached = {}

    def set(self, key, value, *args):
        self.cached[key] = value

    def exists(self, key):
        return key in self.cached


@patch('src.persistence.persist.DBAAS_SENTINEL_ENDPOINT_SIMPLE',
        new_callable=str,
        object='sentinel://fake-host-01:26379,fake-host-02:26379,fake-host-03:26379')
class TestPersist(TestCase):

    @patch('src.persistence.persist.Sentinel')
    def test_connection(self, sentinel_mock, endpoint_mock):
        persistence = Persistence()
        self.assertIsNotNone(persistence.client)
        sentinel_mock.assert_called_once_with([
            ('fake-host-01', '26379'),
            ('fake-host-02', '26379'),
            ('fake-host-03', '26379')
        ], socket_timeout=1)
        self.assertEqual(persistence.ttl_seconds, REDIS_KEY_TTL)

    def test_notified(self, endpoint_mock):
        persistence = Persistence()
        persistence.client = FakeCache()

        task_db = build_task_database()
        task_running = build_task_running()
        persistence.set_notified(task_running)

        self.assertFalse(persistence.was_notified(task_db))
        self.assertTrue(persistence.was_notified(task_running))
