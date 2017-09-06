from unittest import TestCase
from unittest.mock import patch
from requests.auth import HTTPBasicAuth
from src.dbaas.dbaas_api import DBaaS, DBAAS_URL, DBAAS_USER, DBAAS_PASSWORD, \
    DBAAS_HTTPS_VERIFY


class TestDBaaSTasks(TestCase):

    def setUp(self):
        self.api = DBaaS()

    def test_basic_auth(self):
        self.assertEqual(type(self.api._base_auth), HTTPBasicAuth)
        self.assertEqual(self.api._base_auth.username, DBAAS_USER)
        self.assertEqual(self.api._base_auth.password, DBAAS_PASSWORD)

    def test_verify(self):
        self.assertEqual(self.api._verify, DBAAS_HTTPS_VERIFY)

    @patch('src.dbaas.dbaas_api.get')
    def test_get(self, get_method):
        endpoint = 'fake/url'
        self.api.api_get(endpoint)

        final_url = '{}/api/{}'.format(DBAAS_URL, endpoint)
        get_method.assert_called_once_with(
            final_url, auth=self.api._base_auth, verify=self.api._verify
        )

    def latest_tasks_page_size_tests(self, page_size):
        with patch('src.dbaas.dbaas_api.DBaaS.api_get') as api_get_method:
            api_get_method.json.return_value = {'taskhistory': []}
            api_get_method.return_value.status_code = 200

            if page_size:
                self.api.latest_tasks(page_size)
            else:
                self.api.latest_tasks()

            if not page_size:
                page_size = 100

            api_get_method.assert_called_once_with(
                'task/?ordering=-updated_at&page_size={}'.format(page_size)
            )

    def test_latest_tasks_page_size_default(self):
        self.latest_tasks_page_size_tests(None)

    def test_latest_tasks_page_size_bigger(self):
        self.latest_tasks_page_size_tests(150)

    def test_latest_tasks_page_size_small(self):
        self.latest_tasks_page_size_tests(1)

    @patch('src.dbaas.dbaas_api.DBaaS.api_get')
    def test_latest_tasks_content(self, api_get_method):
        api_get_method.return_value.status_code = 200
        api_get_method().json.return_value = {'taskhistory': [
            {
                'id': 1090, 'task_id': 'iiioo-xxxsads', 'task_status': 'ERROR',
                'task_name': 'status.dbaas', 'user': 'admin',
                'object_class': None, 'object_id': None,
                'created_at': '2019-09-12', 'updated_at': '2019-09-13',
            },
            {
                'id': 1091, 'task_id': 'xxxaa-yyyuu', 'task_status': 'RUNNING',
                'task_name': 'database.create', 'user': 'fake.user',
                'object_class': 'logical_database', 'object_id': '123',
                'created_at': '2019-09-13', 'updated_at': '2019-09-14',
            },
        ]}

        tasks = self.api.latest_tasks()
        self.assertEqual(len(tasks), 2)
