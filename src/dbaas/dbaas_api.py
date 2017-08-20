from requests import get
from requests.auth import HTTPBasicAuth
from src.settings import DBAAS_URL, DBAAS_USER, DBAAS_PASSWORD, \
    DBAAS_HTTPS_VERIFY


class DBaaS(object):

    def __init__(self):
        self._base_auth = HTTPBasicAuth(DBAAS_USER, DBAAS_PASSWORD)
        self._verify = DBAAS_HTTPS_VERIFY

    def api_get(self, endpoint):
        final_url = '{}/api/{}'.format(DBAAS_URL, endpoint)
        return get(final_url, auth=self._base_auth, verify=self._verify)

    def latest_tasks(self, page_size=100):
        tasks_url = 'task/?ordering=-id&page_size={}'.format(page_size)
        response = self.api_get(tasks_url)
        content = response.json()

        tasks = []
        for task in content['taskhistory']:
            tasks.append(Task(task))
        return tasks

    def build_task_link(self, task_id):
        return '{}/admin/notification/taskhistory/?task_id={}'.format(
            DBAAS_URL, task_id
        )


class Task(object):

    STATUS_ERROR = 'ERROR'
    DBAAS_TASK_URL = '{}/admin/notification/taskhistory/{}'
    OBJ_CLASS_DATABASE = 'logical_database'

    def __init__(self, api_content):
        self.id = api_content['id']
        self.executor_id = api_content['task_id']
        self.status = api_content['task_status']
        self.name = api_content['task_name'].rsplit('.', 1)[-1]

        self.database_id = None
        if api_content['object_class'] == self.OBJ_CLASS_DATABASE:
            self.database_id = api_content['object_id']

        self.user = api_content['user']
        self.started_at = api_content['created_at']
        self.updated_at = api_content['updated_at']
        self.link = self.DBAAS_TASK_URL.format(DBAAS_URL, self.id)

    @property
    def is_error(self):
        return self.status == self.STATUS_ERROR

    def as_message(self):
        """
            Error in 'database' doing 'resize', by user at 2017-06-11 link
            Error doing 'update_status', at 2017-06-12 link
        """
        message = '{} '.format(self.status.capitalize(), self.name)

        if self.database_id:
            message += 'in \'{}\' '.format(self.database_id)

        message += 'doing \'{}\', '.format(self.name)
        if self.user:
            message += 'by {} '.format(self.user)

        message += 'at {} - {}'.format(self.updated_at, self.link)

        return message
