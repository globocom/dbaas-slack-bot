from logging import info, debug, basicConfig, INFO
from time import sleep
from src.dbaas.dbaas_api import DBaaS
from src.persistence.persist import Persistence
from src.slack.slack_bot import Bot


MAX_DBAAS_ATTEMPS = 10


def main():
    basicConfig(level=INFO)
    bot = Bot()
    dbaas = DBaaS()
    persistence = Persistence()

    info('Loading oldest tasks')
    tasks = dbaas.latest_tasks()
    for task in tasks:
        persistence.set_notified(task)
    info('Loaded')

    errors_count = 0
    while True:
        tasks = []
        try:
            tasks = dbaas.latest_tasks()
        except ConnectionError as e:
            errors_count += 1
            info('Error getting info from DBaaS - {}/{}'.format(
                errors_count, MAX_DBAAS_ATTEMPS
            ))
            debug(e)

            if errors_count == MAX_DBAAS_ATTEMPS:
                bot.send_message(
                    'I can not get task history, '
                    'problem in DBaaS API\n{}'.format(e)
                )
        else:
            errors_count = 0

        for task in tasks:
            if not task.is_error:
                continue

            if not persistence.was_notified(task):
                info('Notifying {}'.format(task.id))
                bot.send_message(task.as_message())

            info('Updating TTL to {}'.format(task.id))
            persistence.set_notified(task)

        sleep(15)


if __name__ == '__main__':
    main()
