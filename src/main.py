## play IdleRPG as a bot

import os
import time
import random

import logging
import logging.config

import idlerpg

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
        logging.warning('!! config file does not exist: %s', config_file)
        return None

    with open(config_file, 'r') as fp:
        conf = yaml.load(fp, Loader=yaml.CLoader)

    if 'Logging' in conf:
        logging.config.dictConfig(conf['Logging'])

    logging.debug('!! config file loaded: %s', config_file)

    return conf

################################################################################
def on_status_update(bot):
    if bot.online is True:
        logging.info('!! IdleBot Online [%s]; next level: %s',
                     bot.rpg_username, bot.next_level)
    else:
        logging.info('!! IdleBot Offline [%s]', bot.rpg_username)

################################################################################
## MAIN ENTRY

args = parse_args()
conf = load_config(args.config)

# fire up the game...
bot = idlerpg.IdleBot(conf['IdleRPG'])

# register event handlers
bot.on_status_update += on_status_update

# let 'er rip
bot.start()

# wait for user to quit (Ctrl-C)
try:
    while 1:
        # use a random sleep value...
        sleep_sec = random.randint(180, 300)
        time.sleep(sleep_sec)

        # keep status current
        bot.request_status()

except KeyboardInterrupt:
    print('anceled by user')

bot.stop()

