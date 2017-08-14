from logging import debug
from healthchecks import bot_check, api_check, persistence_check
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
               "help: For usage info\n  " \
               "status: Check status of all bot services"


class BotMessageStatus(BotMessage):

    @classmethod
    def commands(self):
        return ['status', 'how are you?', 'healthcheck', 'health-check']

    @property
    def message(self):
        api, api_status = api_check()
        bot, bot_status = bot_check()
        persistence, persistence_status = persistence_check()

        total = sum([api, bot, persistence])
        if total == 3:
            message = 'Everything is fine'
        elif total == 2:
            message = 'I\'m with one problem'
        elif total == 1:
            message = 'I\'m in trouble'
        else:
            message = 'Nothing is work, sorry'

        return '{}\nAPI: {}\nSlack: {}\nRedis: {}'.format(
            message, api_status, bot_status, persistence_status
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
