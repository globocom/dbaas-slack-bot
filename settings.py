from os import getenv


SLACK_TOKEN = getenv('SLACK_BOT_TOKEN')

DBAAS_URL = getenv('DBAAS_URL', '127.0.0.1')
DBAAS_USER = getenv('DBAAS_USER', 'dbaas_bot')
DBAAS_PASSWORD = getenv('DBAAS_PASSWORD', 'admin_pwd')
DBAAS_HTTPS_VERIFY = getenv('DBAAS_HTTPS_VERIFY', 'False').upper() == 'TRUE'
