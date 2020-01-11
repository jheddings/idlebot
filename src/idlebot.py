## play IdleRPG as a bot

import os
import time

import logging
import logging.config

import irc

logger = logging.getLogger('IdleBot')

#---------------------------------------------------------------------------
def parse_args():
    import argparse

    argp = argparse.ArgumentParser(description='idlebot: a bot for playing IdleRPG')

    argp.add_argument('--config', default='/etc/idlebot.cfg',
                      help='configuration file (default: /etc/idlebot.cfg)')

    argp.add_argument('params', nargs=argparse.REMAINDER)

    return argp.parse_args()

#---------------------------------------------------------------------------
def load_config(config_file):
    import yaml

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
    client.join(idlerpg_conf['Channel'])

    username = idlerpg_conf['Username']
    password = idlerpg_conf['Password']
    faction = idlerpg_conf['Faction']

    # TODO register if needed
    #client.msg('bot', 'REGISTER {0} {1} {2}'.format(username, password, faction))

    client.msg('bot', 'LOGIN {0} {1}'.format(username, password))

#---------------------------------------------------------------------------
def connect(cfg):
    # configure the client and event handlers
    nickname = cfg['Nickname']
    fullname = cfg['FullName']

    client = irc.Client(nickname, fullname)
    client.on_welcome += on_welcome

    # connect to the IRC server and start to idle...
    irc_server = cfg['Hostname']
    irc_port = cfg['Port']

    client.connect(irc_server, port=irc_port)

    return client

#---------------------------------------------------------------------------
## MAIN ENTRY

args = parse_args()
conf = load_config(args.config)

# TODO verify conf contents
server_conf = conf['Server']
idlerpg_conf = conf['IdleRPG']

# fire up the game...
client = connect(server_conf)

# wait for user to quit (Ctrl-C)
try:
    while 1: time.sleep(1)
except KeyboardInterrupt:
    print('anceled by user')

client.quit()
