from logging import debug
from slackclient import SlackClient
from src.settings import SLACK_TOKEN, SLACK_PROXIES, SLACK_BOT_ID
from src.utils.healthchecks import api_check, bot_check, dbaas_check, \
    persistence_check


class Bot(object):

    def __init__(self):
        self.slack_client = SlackClient(SLACK_TOKEN, SLACK_PROXIES)
        self.name = '<@{}>'.format(SLACK_BOT_ID)

    @property
    def my_channels(self):
        response = self.slack_client.api_call("channels.list")

        channels = []
        for channel in response['channels']:
            if channel['is_member']:
                channels.append(channel['id'])

        return channels

    def send_message_in_channel(self, message, channel):
        self.slack_client.api_call(
            "chat.postMessage", channel=channel, text=message, as_user=True
        )

    def send_message(self, message):
        for channel in self.my_channels:
            self.send_message_in_channel(message, channel)

    def receive_command(self):
        commands = self.slack_client.rtm_read()
        debug(commands)
        return commands

    def get_direct_messages(self):
        commands = self.receive_command()
        if not commands:
            return None

        for command in commands:
            if command['type'] != 'message':
                continue

            if self.name not in command['text']:
                continue

            if command.get('user', '') == SLACK_BOT_ID:
                continue

            text_cleaned = command['text'].replace(self.name, '')
            text_cleaned = text_cleaned.strip()

            yield BotMessage.build(command['channel'], text_cleaned)


class BotMessage(object):

    @classmethod
    def build(cls, channel, text):
        parsed_text = text.lower()
        for klass in cls.__subclasses__():
            if parsed_text in klass.commands():
                return klass(channel, text)

        return BotMessageInvalid(channel, text)

    def __init__(self, channel, text):
        self.channel = channel
        self.text = text

    @classmethod
    def commands(self):
        raise NotImplementedError

    @property
    def message(self):
        raise NotImplementedError

    def __str__(self):
        return '{}-{}'.format(self.channel, self.text)


class BotMessageHelp(BotMessage):

    @classmethod
    def commands(self):
        return ["help"]

    @property
    def message(self):
        return "You can use:\n  " \
               "status: Check status of all bot services"


class BotMessageStatus(BotMessage):

    @classmethod
    def commands(self):
        return ['status', 'how are you?', 'healthcheck', 'health-check']

    @property
    def message(self):
        api, api_status = api_check()
        bot, bot_status = bot_check()
        dbaas, dbaas_status = dbaas_check()
        persistence, persistence_status = persistence_check()

        total = sum([api, bot, dbaas, persistence])
        if total >= 4:
            message = 'Everything is fine'
        elif total >= 3:
            message = 'I\'m with one problem'
        elif total >= 1:
            message = 'I\'m in trouble'
        else:
            message = 'Nothing is working, sorry'

        return '{}\nAPI: {}\nDBaaS: {}\nRedis: {}\nSlack: {}'.format(
            message, api_status, dbaas_status, persistence_status, bot_status
        )


class BotMessageInvalid(BotMessageHelp):

    @classmethod
    def commands(self):
        return []

    @property
    def message(self):
        help_message = super(BotMessageInvalid, self).message
        invalid_message = "I do not understand '{}'".format(self.text)
        return '{}\n{}'.format(invalid_message, help_message)
