## play IdleRPG as a bot

import os
import time
import yaml

import logging
import logging.config

import irc

logger = logging.getLogger('IdleBot')

#---------------------------------------------------------------------------
def load_config(config_file):
    if not os.path.exists(config_file):
        logging.warning('config file does not exist: %s', config_file)
        return None

    with open(config_file, 'r') as fp:
        conf = yaml.load(fp, Loader=yaml.CLoader)

    if 'Logging' in conf:
        logging.config.dictConfig(conf['Logging'])

    logging.debug('config file loaded: %s', config_file)

    return conf

#---------------------------------------------------------------------------
def on_welcome(client, msg):
    client.join(conf['IdleRPG']['Channel'])

    username = conf['IdleRPG']['Username']
    password = conf['IdleRPG']['Password']
    faction = conf['IdleRPG']['Faction']

    # TODO register if needed
    #client.msg('bot', 'REGISTER {0} {1} {2}'.format(username, password, faction))

    client.msg('bot', 'LOGIN {0} {1}'.format(username, password))

#---------------------------------------------------------------------------
## MAIN ENTRY

conf = load_config('idlebot.cfg')

# TODO verify conf contents

# configure the client and event handlers
nickname = conf['Server']['Nickname']
fullname = conf['Server']['FullName']

client = irc.Client(nickname, fullname)
client.on_welcome += on_welcome

# connect to the IRC server and start to idle...
irc_server = conf['Server']['Hostname']
irc_port = conf['Server']['Port']

client.connect(irc_server, port=irc_port)

# wait for user to quit (Ctrl-C)
try:
    while 1: time.sleep(1)
except KeyboardInterrupt:
    print('anceled by user')

client.quit()
