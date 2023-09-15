from flask import Flask, request
from src.slack.slack_bot import Bot, BotDBDev
from src.utils.healthchecks import bot_check, persistence_check


app = Flask('errors_from_api')


@app.route("/healthcheck", methods=['GET'])
def health_check():
    persistence_status, error = persistence_check()
    if not persistence_status:
        return 'WARNING - REDIS - {}'.format(error), 500

    bot_status, error = bot_check()
    if not bot_status:
        return 'WARNING - SLACK - {}'.format(error), 500

    return 'WORKING', 200


@app.route("/healthcheck/api", methods=['GET'])
def health_check_api():
    return 'WORKING', 200


@app.route("/notify", methods=['POST'])
def send_notification():
    content = request.get_json()
    if not content:
        return 'Could not load the json', 400

    message = content.get('message', '')
    if not message:
        return 'Content must have message field', 400

    relevance = content.get('relevance', 'CRITICAL').upper()

    try:
        Bot().send_message(message, relevance)
    except Exception as e:
        return e, 400
    else:
        return 'OK', 201


@app.route("/alerta", methods=['GET'])
def send_message_to_dbdev_get():
    content = request.args
    if not content:
        return 'Could not load the json', 400

    message = content.get('m', '')
    if not message:
        return 'Content must have message field', 400

    try:
        BotDBDev().send_message_in_channel(message)
    except Exception as e:
        return e, 400
    return 'OK', 201


@app.route("/alerta", methods=['POST'])
def send_message_to_dbdev_post():
    content = request.get_json()
    if not content:
        return 'Could not load the json', 400

    message = content.get('message', '')
    if not message:
        return 'Content must have message field', 400

    channel_id = None
    if content.get('channel_id', '1') != '1':
        channel_id = content.get('channel_id')


    try:
        BotDBDev().send_message_in_channel(message, channel_id)
    except Exception as e:
        return e, 400
    return 'OK', 201


if __name__ == "__main__":
    app.run(host='0.0.0.0')
