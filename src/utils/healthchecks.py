
def persistence_check():
    from random import randint
    from src.persistence.persist import Persistence

    key, value = 'HEALTH_CHECK', randint(0, 100000)
    try:
        persistence = Persistence()
        persistence.client.set(key, value)
        assert int(persistence.client.get(key)) == value
        persistence.client.delete(key)
    except Exception as e:
        return False, e
    else:
        return True, 'OK'


def bot_check():
    from src.slack.slack_bot import Bot
    try:
        bot = Bot()
        assert len(bot.my_channels) > 0
    except Exception as e:
        return False, e
    else:
        return True, 'OK'


def api_check():
    from requests import get
    from src.settings import API_ENDPOINT

    try:
        response = get(API_ENDPOINT + '/healthcheck/api')
        assert response.text == 'WORKING'
    except Exception as e:
        return False, e
    else:
        return True, 'OK'


def dbaas_check():
    from src.dbaas.dbaas_api import DBaaS

    try:
        assert len(DBaaS().latest_tasks(page_size=1)) == 1
    except Exception as e:
        return False, e
    else:
        return True, 'OK'
