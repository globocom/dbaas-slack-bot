from logging import info, basicConfig, INFO
from time import sleep
from src.slack.slack_bot import Bot


def main():
    basicConfig(level=INFO)
    bot = Bot()

    info('Connection Slack')
    if not bot.slack_client.rtm_connect():
        info('Could not connect in web_socket')
        exit()
    else:
        info('Connected')

    while True:
        sleep(1)
        for message in bot.get_direct_messages():
            info(message)
            bot.send_message_in_channel(message.message, message.channel)


if __name__ == '__main__':
    main()
