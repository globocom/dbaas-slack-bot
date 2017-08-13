from logging import debug
from slackclient import SlackClient
from settings import SLACK_TOKEN, SLACK_PROXIES, SLACK_BOT_ID


class Bot(object):

    def __init__(self):
        self.slack_client = SlackClient(SLACK_TOKEN, SLACK_PROXIES)

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

    def get_messages(self):
        commands = self.receive_command()
        if not commands:
            return None

        for command in commands:
            if command['type'] != 'message':
                continue

            if command.get('bot_id', '') == SLACK_BOT_ID:
                continue

            yield BotMessage.build(command['channel'], command['text'])


class BotMessage(object):

    @classmethod
    def build(cls, channel, text):
        parsed_text = text.lower()
        for klass in cls.__subclasses__():
            if parsed_text in klass.commands:
                return klass(channel, text)

        return BotMessageInvalid(channel, text)

    def __init__(self, channel, text):
        self.channel = channel
        self.text = text

    @property
    def commands(self):
        raise NotImplementedError

    @property
    def message(self):
        raise NotImplementedError

    def __str__(self):
        return '{}-{}'.format(self.channel, self.text)


class BotMessageHelp(BotMessage):

    @property
    def commands(self):
        return ["help"]

    @property
    def message(self):
        return \
            """
            You can use:
            help: For usage info
            status: Check all bot services status
            """


class BotMessageStatus(BotMessage):

    @property
    def commands(self):
        return ['status', 'how are you?', 'healthcheck', 'health-check']

    @property
    def message(self):
        return \
            """
            Everything is good like a sun day
            Redis:
            Slack:
            API:
            """


class BotMessageInvalid(BotMessageHelp):

    @property
    def commands(self):
        return []

    @property
    def message(self):
        help_message = super(BotMessageInvalid, self).message
        invalid_message = "I do not understand '{}'".format(self.text)
        return '{}\n{}'.format(invalid_message, help_message)
