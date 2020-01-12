## bot for playing IdleRPG
# http://idlerpg.net/source.php

import re
import logging
import datetime

import irc

# for parsing server messages...
logon_notice_re = re.compile('(.+), the level ([0-9]+) (.+), is now online')
online_status_re = re.compile('You are (.+), the level ([0-9]+) (.+)\.')
next_level_re = re.compile('Next level in ([0-9]+) days, ([0-9]+):([0-9]+):([0-9]+)')

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
        if self._parse_login_notice(txt):
            self.logger.info('Bot Online [%d] => %s', self.level, self.next)

        elif self._parse_online_status(txt):
            self.logger.debug('status - Online [%d] => %s', self.level, self.next)

        elif self._parse_offline_status(txt):
            self.logger.debug('status - Offline')

    #---------------------------------------------------------------------------
    def start(self):
        self.client.connect(self.irc_server, port=self.irc_port)

    #---------------------------------------------------------------------------
    def stop(self):
        if self.client.connected is True:
            # clean everything up gracefully
            self.client.msg(self.rpg_bot, 'LOGOUT')
            self.client.part(self.rpg_channel, 'goodbye')
            self.client.quit()

        self.online = False

    #---------------------------------------------------------------------------
    def request_status(self):
        # status requsts are async...  the bot will send a privmsg back, which
        # is where we parse the actuall status.

        # TODO how do we detect if the bot never replies?

        if self.client.connected is True:
            self.client.msg('bot', 'WHOAMI')
        else:
            self.online = False

    #---------------------------------------------------------------------------
    def _parse_next_level(self, msg):
        m = next_level_re.search(msg)
        if m is None: return None

        days = int(m.group(1))
        hours = int(m.group(2))
        minutes = int(m.group(3))
        seconds = int(m.group(4))

        return datetime.timedelta(days, seconds, 0, 0, minutes, hours)

    #---------------------------------------------------------------------------
    def _parse_login_notice(self, msg):
        m = logon_notice_re.match(msg)
        if m is None: return False

        msg_user = m.group(1)
        if msg_user == self.rpg_username:
            self.online = True
            self.level = int(m.group(2))
            self.next = self._parse_next_level(msg)

        return True

    #---------------------------------------------------------------------------
    def _parse_online_status(self, msg):
        m = online_status_re.match(msg)
        if m is None: return False

        msg_user = m.group(1)
        if msg_user == self.rpg_username:
            self.online = True
            self.level = int(m.group(2))
            self.next = self._parse_next_level(msg)

        return True

    #---------------------------------------------------------------------------
    def _parse_offline_status(self, msg):
        if not msg.startswith('You are not logged in'):
            return False

        self.online = False

        return True

