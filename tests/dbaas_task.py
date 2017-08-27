from unittest import TestCase
from src.dbaas.dbaas_api import Task, DBAAS_URL
from tests import OBJ_CLASS_DATABASE, build_task_database, build_task_running


class TestDBaaSTasks(TestCase):

    TASK_LINK = '{}/admin/notification/taskhistory/{}'

    def setUp(self):
        self.task = build_task_running()
        self.task_db = build_task_database()

    def test_task_error_value(self):
        self.assertEqual(Task.STATUS_ERROR, 'ERROR')

    def test_task_link_value(self):
        self.assertEqual(Task.DBAAS_TASK_URL, self.TASK_LINK)

    def test_task_database_class_value(self):
        self.assertEqual(Task.OBJ_CLASS_DATABASE, OBJ_CLASS_DATABASE)

    def test_task_link(self):
        task_url = self.TASK_LINK.format(DBAAS_URL, self.task.id)
        task_url_db = self.TASK_LINK.format(DBAAS_URL, self.task_db.id)
        self.assertEqual(self.task.link, task_url)
        self.assertEqual(self.task_db.link, task_url_db)

    def test_task_is_error(self):
        self.assertFalse(self.task.is_error)
        self.task.status = Task.STATUS_ERROR
        self.assertTrue(self.task.is_error)

    def test_task_db(self):
        self.assertEqual(self.task.database_id, None)
        self.assertEqual(self.task_db.database_id, 123)

    def test_message_database(self):
        self.assertEqual(
            self.task_db.as_message(),
            "{} in '{}' doing '{}', by {} at {} - {}".format(
                self.task_db.status.capitalize(),
                self.task_db.database_id,
                self.task_db.name,
                self.task_db.user,
                self.task_db.updated_at,
                self.task_db.link
            )
        )

    def test_message_without_database(self):
        self.assertEqual(
            self.task.as_message(),
            "{} doing '{}', by {} at {} - {}".format(
                self.task.status.capitalize(),
                self.task.name,
                self.task.user,
                self.task.updated_at,
                self.task.link
            )
        )

    def test_message_database_without_user(self):
        self.task_db.user = None
        self.assertEqual(
            self.task_db.as_message(),
            "{} in '{}' doing '{}', at {} - {}".format(
                self.task_db.status.capitalize(),
                self.task_db.database_id,
                self.task_db.name,
                self.task_db.updated_at,
                self.task_db.link
            )
        )

    def test_message_without_database_and_user(self):
        self.task.user = None
        self.assertEqual(
            self.task.as_message(),
            "{} doing '{}', at {} - {}".format(
                self.task.status.capitalize(),
                self.task.name,
                self.task.updated_at,
                self.task.link
            )
        )
