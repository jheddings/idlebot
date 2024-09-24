## bot for playing IdleRPG
# http://idlerpg.net/source.php

import logging
import re
from datetime import datetime

from . import irc
from .config import AppConfig, IRCConfig, PlayerConfig
from .player import PlayerInfo

# for parsing server messages...
online_status_re = re.compile(r"You are (.+), the level ([0-9]+) (.+)\.")
next_level_re = re.compile(r"Next level in ([0-9]+) days?, ([0-9]+):([0-9]+):([0-9]+)")

logger = logging.getLogger(__name__)


class IdleBot:
    def __init__(self, conf: AppConfig):
        self.logger = logger.getChild("IdleBot")

        self.rpg_channel = conf.idlerpg.game_channel
        self.rpg_bot = conf.idlerpg.game_bot

        self._pending_status_request = None

        self._initialize_client(conf.irc)

        self._player = None
        self._config = conf

    def _initialize_client(self, conf: IRCConfig):
        self.irc_server = conf.server
        self.irc_port = conf.port

        self.client = irc.Client(conf.nickname, conf.fullname)
        self.client.on_welcome += self._on_welcome
        self.client.on_notice += self._on_notice

    def start(self):
        self.client.connect(self.irc_server, port=self.irc_port)

    def stop(self):
        if self.client.connected is True:
            # clean everything up gracefully
            self.client.msg(self.rpg_bot, "LOGOUT")
            self.client.part(self.rpg_channel, "goodbye")
            self.client.quit()

        self._player = None

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
            self.client.msg(self.rpg_bot, "WHOAMI")
            self._pending_status_request = datetime.now()
        else:
            self._player = None

    def _register_player(self, player: PlayerConfig):
        self.logger.info("registering new player: %s", player.name)
        register = f"REGISTER {player.name} {player.password} {player.class_}"
        self.client.msg(self.rpg_bot, register)

    def _join_rpg_game(self, client: irc.Client):
        pcfg = self._config.player

        self.logger.info(
            "joining IdleRPG: %s [%s]",
            self.rpg_channel,
            pcfg.name,
        )

        login_msg = f"LOGIN {pcfg.name} {pcfg.password}"

        client.join(self.rpg_channel)
        client.msg(self.rpg_bot, login_msg)

    def _parse_no_account_notice(self, msg):
        if msg.startswith("Sorry, no such account name."):
            self._register_player(self._config.player)
            return True

        return False

    def _parse_login_notice(self, msg):
        if msg.startswith("Logon successful."):
            self._refresh_player_status()
            return True

        return False

    def _refresh_player_status(self):
        if self._player is None:
            self._player = PlayerInfo.get(self._config.player.name)
        else:
            self._player.update()

        print(self._player)

        self.logger.info(
            "status [%s] -- online:%s level:%s next:%s",
            self._player.username,
            self._player.online,
            self._player.ttl,
        )

    def _on_welcome(self, client: irc.Client, txt):
        self.logger.debug("welcome received")
        self._join_rpg_game(client)

    def _on_notice(self, client: irc.Client, origin, recip, txt):
        if self._parse_no_account_notice(txt):
            return
        if self._parse_login_notice(txt):
            return
