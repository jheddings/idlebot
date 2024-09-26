## bot for playing IdleRPG
# http://idlerpg.net/source.php

import logging

from . import irc
from .config import AppConfig, IRCConfig, PlayerConfig
from .player import PlayerInfo

logger = logging.getLogger(__name__)


class IdleBot:
    def __init__(self, conf: AppConfig):
        self.logger = logger.getChild("IdleBot")

        self.rpg_channel = conf.idlerpg.game_channel
        self.rpg_bot = conf.idlerpg.game_bot

        self._pending_status_request = None

        self._initialize_client(conf.irc)

        self._config = conf

    def _initialize_client(self, conf: IRCConfig):
        self.irc_server = conf.server
        self.irc_port = conf.port

        self.client = irc.Client(conf.nickname, conf.fullname)
        self.client.on_welcome += self._on_welcome
        self.client.on_privmsg += self._on_privmsg
        self.client.on_notice += self._on_notice
        self.client.on_ping += self._on_ping

    def start(self):
        self.client.connect(self.irc_server, port=self.irc_port)

    def stop(self):
        if self.client.connected is True:
            # clean everything up gracefully
            self.client.msg(self.rpg_bot, "LOGOUT")
            self.client.part(self.rpg_channel, "goodbye")
            self.client.quit()

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

    def _refresh_player_status(self):
        # NOTE this status is often behind the actual game
        player = PlayerInfo.get(self._config.player.name)

        self.logger.info(
            "You are %s, the level %d %s. Next level in %s [%s].",
            player.username,
            player.level,
            player.character,
            player.ttl,
            "online" if player.is_online else "offline",
        )

    def _on_welcome(self, client: irc.Client, txt):
        self.logger.debug("welcome received")
        self._join_rpg_game(client)

    def _on_notice(self, client: irc.Client, origin, recip, txt):
        if txt.startswith("Sorry, no such account"):
            self._register_player(self._config.player)

        elif txt.startswith("Logon successful."):
            self._refresh_player_status()

    def _on_privmsg(self, client: irc.Client, origin, recip, txt):
        self.logger.debug("privmsg [%s]: %s", recip, txt)

    def _on_ping(self, client, txt):
        self._refresh_player_status()
