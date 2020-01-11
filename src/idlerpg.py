## bot for playing IdleRPG
# http://idlerpg.net/source.php

import re
import logging
import datetime

import irc

# for parsing server messages...
online_status_re = re.compile('You are (.*), the level ([0-9]+) (.+)\..* ([0-9]+) days, ([0-9]+):([0-9]+):([0-9]+)$')

################################################################################
class IdleBot():

    #---------------------------------------------------------------------------
    def __init__(self, conf):
        self.logger = logging.getLogger('idlerpg.IdleBot')

        self.irc_server = conf['irc_server']
        self.irc_port = int(conf['irc_port'])
        #self.irc_passwd = conf['irc_passwd']

        self.irc_nickname = conf['irc_nickname']
        self.irc_fullname = conf['irc_fullname']

        self.rpg_channel = conf['game_channel']
        self.rpg_bot = conf['game_bot']

        self.rpg_username = conf['player_name']
        self.rpg_password = conf['player_passwd']
        self.rpg_class = conf['player_class']

        self.online = False
        self.next = None
        self.level = None

        self.client = irc.Client(self.irc_nickname, self.irc_fullname)
        self.client.on_welcome += self.on_welcome
        self.client.on_privmsg += self.on_privmsg

    #---------------------------------------------------------------------------
    def on_welcome(self, client, txt):
        self.logger.debug('welcome received... joining IdleRPG')

        client.join(self.rpg_channel)

        # TODO register if needed
        #client.msg('bot', 'REGISTER {0} {1} {2}'.format(username, password, faction))

        login_msg = 'LOGIN ' + self.rpg_username + ' ' + self.rpg_password
        client.msg(self.rpg_bot, login_msg)

    #---------------------------------------------------------------------------
    def on_privmsg(self, client, origin, recip, txt):
        if self._parse_online_msg(txt):
            self.logger.debug('status - Online [%d] => %s', self.level, self.next)

        elif self._parse_offline_msg(txt):
            self.logger.debug('status - Offline')

    #---------------------------------------------------------------------------
    def start(self):
        self.client.connect(self.irc_server, port=self.irc_port)

    #---------------------------------------------------------------------------
    def stop(self):
        if self.client.connected is True:
            # parting causes quite a penalty...
            self.client.part(self.rpg_channel, 'goodbye')

            # close everything up
            self.client.quit()

        self.online = False

    #---------------------------------------------------------------------------
    def request_status(self):
        if self.client.connected is not True:
            self.online = False

        # this will cause the server to respond for parsing in on_privmsg
        self.client.msg('bot', 'WHOAMI')

    #---------------------------------------------------------------------------
    def _parse_online_msg(self, msg):
        m = online_status_re.match(msg)
        if m is None: return False

        self.online = (m.group(1) == self.rpg_username)
        self.level = int(m.group(2))

        days = int(m.group(4))
        hours = int(m.group(5))
        minutes = int(m.group(6))
        seconds = int(m.group(7))

        self.next = datetime.timedelta(days, seconds, 0, 0, minutes, hours)

        return True

    #---------------------------------------------------------------------------
    def _parse_offline_msg(self, msg):
        if not msg.startswith('You are not logged in'):
            return False

        self.online = False

        return True

