from time import sleep
from logging import info
from slack_bot import Bot
from dbaas_api import DBaaS


def main():
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

            notified[task_id] = True

        for task_id, founded in notified.items():
            if not founded:
                notified.pop(task_id)
            else:
                notified[task_id] = False

        info('Size of notified: {}'.format(len(notified)))
        sleep(15)


if __name__ == '__main__':
    main()
