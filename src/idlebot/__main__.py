"""An IRC bot for playing IdleRPG."""

import logging
import random
import time

import click

from . import idlerpg, version
from .config import AppConfig

logger = logging.getLogger(__name__)


class MainApp:
    """Context used during main execution."""

    def __init__(self, config: AppConfig):
        self.logger = logger.getChild("MainApp")

        self.config = config

        self._initialize_bot()

    def _initialize_bot(self):
        # fire up the game...
        self.bot = idlerpg.IdleBot(self.config)

        # register event handlers
        self.bot.on_status_update += self.on_status_update

    def __call__(self):
        # let 'er rip
        self.bot.start()

        # wait for user to quit (Ctrl-C)
        try:
            while 1:
                # use a random sleep value...
                sleep_sec = random.randint(180, 300)
                time.sleep(sleep_sec)

                # keep status current
                self.bot.request_status()

        except KeyboardInterrupt:
            print("anceled by user")

        self.bot.stop()

    def on_status_update(self, bot: idlerpg.IdleBot):
        if bot.online is True:
            self.logger.info(
                "!! IdleBot Online [%s]; next level: %s",
                bot.rpg_username,
                bot.next_level,
            )
        else:
            self.logger.info("!! IdleBot Offline [%s]", bot.rpg_username)


@click.command()
@click.option(
    "--config",
    "-f",
    default="idlebot.yaml",
    help="app config file (default: idlebot.yaml)",
)
@click.version_option(
    version=version.__version__,
    package_name=version.__pkgname__,
    prog_name=version.__pkgname__,
)
def main(config):
    cfg = AppConfig.load(config)

    app = MainApp(cfg)

    app()


### MAIN ENTRY
if __name__ == "__main__":
    main()
