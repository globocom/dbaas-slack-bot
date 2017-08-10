from time import sleep
from logging import info, basicConfig, INFO
from slack_bot import Bot
from dbaas_api import DBaaS


def main():
    basicConfig(level=INFO)
    bot = Bot()
    dbaas = DBaaS()
    notified = {}

    while True:
        tasks = dbaas.latest_tasks()
        for task_id, task_status in tasks.items():
            if task_status != 'ERROR':
                continue

            if task_id not in notified:
                task_link = dbaas.build_task_link(task_id)
                bot.send_message('Error: {}'.format(task_link))

            notified[task_id] = 3000

        for task_id, ttl in notified.items():
            ttl -= 1
            notified[task_id] = ttl

            if ttl <= 0:
                info('Removing notified {}...'.format(task_id))
                notified.pop(task_id)

        info('Size of notified: {}'.format(len(notified)))
        sleep(15)


if __name__ == '__main__':
    main()
