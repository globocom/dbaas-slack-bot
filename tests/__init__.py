from src.dbaas.dbaas_api import Task


OBJ_CLASS_DATABASE = 'logical_database'


def build_task(
        task_id, executor_id, status, name, obj_class, obj_id, user,
        created_at, updated_at
):
    task = Task({
        'id': task_id,
        'task_id': executor_id,
        'task_status': status,
        'task_name': name,
        'object_class': obj_class,
        'object_id': obj_id,
        'user': user,
        'created_at': created_at,
        'updated_at': updated_at,
    })

    assert task.id == task_id
    assert task.executor_id == executor_id
    assert task.status == status
    assert task.name in name

    if obj_class == OBJ_CLASS_DATABASE:
        assert task.database_id  == obj_id
    else:
        assert task.database_id == None

    assert task.user == user
    assert task.started_at == created_at
    assert task.updated_at == updated_at

    return task

def build_task_running():
    return build_task(
        100, 'xxx-yyy', 'RUNNING', 'notification.tasks.status',
        None, None, 'admin', '2017-01-20', '2017-01-21'
    )

def build_task_database():
    return build_task(
        120, 'zzz-ooo', 'SUCCESS', 'database.operations.resize',
        'logical_database', 123, 'dbaas_user', '2017-03-22', '2017-03-23',
    )
