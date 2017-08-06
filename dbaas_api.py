from requests import get
from requests.auth import HTTPBasicAuth
from settings import DBAAS_URL, DBAAS_USER, DBAAS_PASSWORD, DBAAS_HTTPS_VERIFY


class DBaaS(object):

    def __init__(self):
        self._base_auth = HTTPBasicAuth(DBAAS_USER, DBAAS_PASSWORD)
        self._verify = DBAAS_HTTPS_VERIFY

    def api_get(self, endpoint):
        final_url = '{}/api/{}'.format(DBAAS_URL, endpoint)
        return get(final_url, auth=self._base_auth, verify=self._verify)

    def latest_tasks(self):
        response = self.api_get('task')
        content = response.json()

        tasks = {}
        for task in content['taskhistory']:
            tasks[task['task_id']] = task['task_status']

        return tasks

    def build_task_link(self, task_id):
        return '{}/admin/notification/taskhistory/?task_id={}'.format(
            DBAAS_URL, task_id
        )
