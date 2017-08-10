from slackclient import SlackClient
from settings import SLACK_TOKEN, SLACK_PROXIES


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
