from requests import get
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError
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
        tasks_url = 'task/?ordering=-updated_at&page_size={}'.format(page_size)
        response = self.api_get(tasks_url)

        if response.status_code != 200:
            raise ConnectionError(
                'Problem with DBaaS api\n{}-{}'.format(
                    response.status_code, response.content
                )
            )

        content = response.json()

        tasks = []
        for task in content['taskhistory']:
            tasks.append(Task(task))
        return tasks


class Task(object):

    STATUS_ERROR = 'ERROR'
    DBAAS_TASK_URL = '{}/admin/notification/taskhistory/{}'
    OBJ_CLASS_DATABASE = 'logical_database'

    def __init__(self, api_content):
        self.id = api_content['id']
        self.executor_id = api_content['task_id']
        self.status = api_content['task_status']

        self.name = api_content['task_name']
        if '.' in self.name:
            self.name = self.name.rsplit('.', 1)[-1]

        self.database = Database.build(api_content)
        self.user = api_content['user']
        self.started_at = api_content['created_at']
        self.updated_at = api_content['updated_at']
        self.link = self.DBAAS_TASK_URL.format(DBAAS_URL, self.id)
        self.relevance = api_content.get('relevance', 'CRITICAL')

    @property
    def is_error(self):
        return self.status == self.STATUS_ERROR

    def as_message(self):
        """
            Error in 'database' doing 'resize', by user at 2017-06-11 link
            Error doing 'update_status', at 2017-06-12 link
        """
        message = '{} '.format(self.status.capitalize(), self.name)

        if self.database:
            message += 'in \'{}\' '.format(self.database)

        message += 'doing \'{}\', '.format(self.name)
        if self.user:
            message += 'by {} '.format(self.user)

        message += 'at {} - {}'.format(self.updated_at, self.link)

        return message


class Database(object):

    @classmethod
    def build(cls, api_content):
        if api_content['object_class'] != Task.OBJ_CLASS_DATABASE:
            return

        db_id = api_content['object_id']

        database_details = api_content['database']
        if type(database_details) != dict:
            return Database(db_id)

        name = database_details['name']
        engine = database_details['engine']
        environment = database_details['environment']
        return Database(db_id, name, engine, environment)

    def __init__(self, db_id, name=None, engine=None, environment=None):
        self.db_id = db_id
        self.name = name
        self.engine = engine
        self.environment = environment

    def __str__(self):
        """
            database_id
            database_name(engine/env)
        """

        database = self.name if self.name else str(self.db_id)

        attributes = []
        if self.engine:
            attributes.append(self.engine)

        if self.environment:
            attributes.append(self.environment)

        if attributes:
            database += '({})'.format('/'.join(attributes))

        return database


