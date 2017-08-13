from random import randint
from requests import get
from persist import Persistence
from settings import API_ENDPOINT
from slack_bot import Bot


def persistence_check():
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
    try:
        bot = Bot()
        assert len(bot.my_channels) > 0
    except Exception as e:
        return False, e
    else:
        return True, 'OK'


def api_check():
    try:
        response = get(API_ENDPOINT + '/healthcheck/api')
        assert response.text == 'WORKING'
    except Exception as e:
        return False, e
    else:
        return True, 'OK'
