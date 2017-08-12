from time import sleep
from logging import info, basicConfig, INFO
from slack_bot import Bot


def main():
    basicConfig(level=INFO)
    bot = Bot()

    info('Connection Slack')
    bot.slack_client.rtm_connect()
    info('Connected')

    while True:
        sleep(0.5)
        for message in bot.get_messages():
            info(message)
            bot.send_message_in_channel(message.message, message.channel)


if __name__ == '__main__':
    main()
