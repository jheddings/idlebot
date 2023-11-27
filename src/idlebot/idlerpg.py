## bot for playing IdleRPG
# http://idlerpg.net/source.php

import logging
import re
from datetime import datetime, timedelta

from . import irc

# for parsing server messages...
online_status_re = re.compile(r"You are (.+), the level ([0-9]+) (.+)\.")
next_level_re = re.compile(r"Next level in ([0-9]+) days?, ([0-9]+):([0-9]+):([0-9]+)")


# Events => Handler Function
#   on_status_update => func(bot)
class IdleBot:
    def __init__(self, conf):
        self.logger = logging.getLogger("idlerpg.IdleBot")

        self.irc_server = conf["irc_server"]
        self.irc_port = int(conf["irc_port"])

        self.irc_nickname = conf["irc_nickname"]
        self.irc_fullname = conf["irc_fullname"]

        self.rpg_channel = conf["game_channel"]
        self.rpg_bot = conf["game_bot"]

        self.rpg_username = conf["player_name"]
        self.rpg_password = conf["player_passwd"]
        self.rpg_class = conf["player_class"]

        self.online = False
        self.level = None
        self.next_level = None

        self.on_status_update = irc.Event()

        self._pending_status_request = None

        self.client = irc.Client(self.irc_nickname, self.irc_fullname)
        self.client.on_welcome += self._on_welcome
        self.client.on_privmsg += self._on_privmsg
        self.client.on_notice += self._on_notice

    def start(self):
        self.client.connect(self.irc_server, port=self.irc_port)

    def stop(self):
        if self.client.connected is True:
            # clean everything up gracefully
            self.client.msg(self.rpg_bot, "LOGOUT")
            self.client.part(self.rpg_channel, "goodbye")
            self.client.quit()

        self.online = False

    # send a status request to the server.  since this will message the game bot,
    # be careful calling this excessively as it may be flagged as malicious
    def request_status(self):
        if self.client.connected is not True:
            raise ConnectionError("not connected")

        # TODO how do we detect if the bot never replies?
        if self._pending_status_request is not None:
            return

        # request our current level from the game bot
        if self.client.connected is True:
            self.client.msg("bot", "WHOAMI")
            self._pending_status_request = datetime.now()
        else:
            self.online = False

    def _parse_next_level(self, msg):
        m = next_level_re.search(msg)
        if m is None:
            return None

        days = int(m.group(1))
        hours = int(m.group(2))
        minutes = int(m.group(3))
        seconds = int(m.group(4))

        return timedelta(days, seconds, 0, 0, minutes, hours)

    def _parse_no_account_notice(self, msg):
        if not msg.startswith("Sorry, no such account name."):
            return False

        register_msg = "REGISTER"
        register_msg += " " + self.rpg_username
        register_msg += " " + self.rpg_password
        register_msg += " " + self.rpg_class

        self.client.msg("bot", register_msg)

        return True

    def _parse_login_notice(self, msg):
        if not msg.startswith("Logon successful."):
            return False

        nxtlvl = self._parse_next_level(msg)

        self._update_status(True, False, nxtlvl)

        return True

    def _parse_online_status(self, msg):
        m = online_status_re.match(msg)
        if m is None:
            return False

        msg_user = m.group(1)

        # the message parsed, but it is not about us...
        if msg_user != self.rpg_username:
            return True

        level = int(m.group(2))
        nxtlvl = self._parse_next_level(msg)

        self._update_status(True, level, nxtlvl)
        self._pending_status_request = None

        return True

    def _parse_offline_status(self, msg):
        if not msg.startswith("You are not logged in"):
            return False

        self._update_status(False, None, None)

        return True

    def _update_status(self, online=None, level=False, nxtlvl=False):
        dirty = False

        if online is not None and self.online != online:
            self.online = online
            dirty = True

        if level is not False and self.level != level:
            self.level = level
            dirty = True

        if nxtlvl is not False and self.next_level != nxtlvl:
            self.next_level = nxtlvl
            dirty = True

        # TODO improve debug logging for status changes
        self.logger.debug(
            "status [%s] -- online:%s level:%s next:%s",
            self.rpg_username,
            self.online,
            self.level,
            self.next_level,
        )

        # XXX do we need to be worried about a dirty flag since the next_level
        # status will most often change on any of the regular updates?
        if dirty:
            self.on_status_update(self)

    def _on_welcome(self, client, txt):
        self.logger.debug("welcome received... joining IdleRPG")

        client.join(self.rpg_channel)

        login_msg = "LOGIN"
        login_msg += " " + self.rpg_username
        login_msg += " " + self.rpg_password

        client.msg(self.rpg_bot, login_msg)

    def _on_notice(self, client, origin, recip, txt):
        if self._parse_no_account_notice(txt):
            return
        if self._parse_login_notice(txt):
            return

    def _on_privmsg(self, client, origin, recip, txt):
        if self._parse_online_status(txt):
            return
        if self._parse_offline_status(txt):
            return
