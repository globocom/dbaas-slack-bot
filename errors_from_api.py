from random import randint
from flask import Flask, abort, request, json
from slack_bot import Bot
from persist import Persistence


app = Flask(__name__)


@app.route("/healthcheck", methods=['GET'])
def health_check():
    key, value = 'HEALTH_CHECK', randint(0, 100000)
    try:
        persistence = Persistence()
        persistence.client.set(key, value)
        assert int(persistence.client.get(key)) == value
        persistence.client.delete(key)
    except Exception as e:
        return 'WARNING - REDIS - {}'.format(e), 500

    try:
        bot = Bot()
        assert len(bot.my_channels) > 0
    except Exception as e:
        return 'WARNING - SLACK - {}'.format(e), 500

    return 'WORKING', 200


@app.route("/notify", methods=['POST'])
def send_notification():
    content = request.get_json()
    message = content.get('message', '')
    if not message:
        return 'Content must have message field', 400

    try:
        Bot().send_message(message)
    except Exception as e:
        return e, 400
    else:
        return 'OK', 201


if __name__ == "__main__":
    app.run(debug=True)
