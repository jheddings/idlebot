## bot for playing IdleRPG
# http://idlerpg.net/source.php

import logging
import re
from datetime import datetime, timedelta

from idlebot.metrics import AppMetrics

from . import irc
from .config import AppConfig, IRCConfig

# for parsing server messages...
online_status_re = re.compile(r"You are (.+), the level ([0-9]+) (.+)\.")
next_level_re = re.compile(r"Next level in ([0-9]+) days?, ([0-9]+):([0-9]+):([0-9]+)")

logger = logging.getLogger(__name__)


class IdleBot:
    def __init__(self, conf: AppConfig):
        self.logger = logger.getChild("IdleBot")

        self.rpg_channel = conf.idlerpg.game_channel
        self.rpg_bot = conf.idlerpg.game_bot

        self.rpg_username = conf.player.name
        self.rpg_password = conf.player.password
        self.rpg_class = conf.player.class_

        self.online = False
        self.level = None
        self.next_level = None

        self._pending_status_request = None

        self._initialize_client(conf.irc)

        self.metrics = AppMetrics(self)

    def _initialize_client(self, conf: IRCConfig):
        self.irc_server = conf.server
        self.irc_port = conf.port

        self.client = irc.Client(conf.nickname, conf.fullname)
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

        # TODO increment an error metric
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

    def _update_status(self, online=False, level=None, nxtlvl=None):
        self.online = online
        self.metrics.status.set(online)

        if level is not None:
            self.level = level
            self.metrics.current_level.set(level)

        if nxtlvl is not None:
            self.next_level = nxtlvl
            self.metrics.next_level.set(nxtlvl.total_seconds())

        self.logger.debug(
            "status [%s] -- online:%s level:%s next:%s",
            self.rpg_username,
            self.online,
            self.level,
            self.next_level,
        )

    def _on_welcome(self, client: irc.Client, txt):
        self.logger.debug("welcome received... joining IdleRPG")

        client.join(self.rpg_channel)

        login_msg = "LOGIN"
        login_msg += " " + self.rpg_username
        login_msg += " " + self.rpg_password

        client.msg(self.rpg_bot, login_msg)

    def _on_notice(self, client: irc.Client, origin, recip, txt):
        if self._parse_no_account_notice(txt):
            return
        if self._parse_login_notice(txt):
            return

    def _on_privmsg(self, client: irc.Client, origin, recip, txt):
        if self._parse_online_status(txt):
            return
        if self._parse_offline_status(txt):
            return
