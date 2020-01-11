## play IdleRPG as a bot

import os
import time

import logging
import logging.config

import idlerpg

logger = logging.getLogger('IdleBot')

################################################################################
def parse_args():
    import argparse

    argp = argparse.ArgumentParser(description='idlebot: a bot for playing IdleRPG')

    argp.add_argument('--config', default='/etc/idlebot.cfg',
                      help='configuration file (default: /etc/idlebot.cfg)')

    argp.add_argument('params', nargs=argparse.REMAINDER)

    return argp.parse_args()

################################################################################
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

################################################################################
## MAIN ENTRY

args = parse_args()
conf = load_config(args.config)

# fire up the game...
bot = idlerpg.IdleBot(conf['IdleRPG'])
bot.start()

# wait for user to quit (Ctrl-C)
try:
    while 1:
        bot.request_status()
        time.sleep(60)
except KeyboardInterrupt:
    print('anceled by user')

bot.stop()
