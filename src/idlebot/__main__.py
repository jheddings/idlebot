"""An IRC bot for playing IdleRPG."""

import logging
import random
import time

import click
from prometheus_client import start_http_server

from . import idlerpg, version
from .config import AppConfig

logger = logging.getLogger(__name__)


class MainApp:
    """Context used during main execution."""

    def __init__(self, config: AppConfig):
        self.logger = logger.getChild("MainApp")

        self.config = config

        self._initialize_bot()
        self._initialize_metrics(config.metrics)

    def _initialize_bot(self):
        # fire up the game...
        self.bot = idlerpg.IdleBot(self.config)

    def _initialize_metrics(self, port=None):
        if port is None:
            self.logger.debug("metrics server disabled by config")
        else:
            self.logger.info("Initializing app metrics: %d", port)
            start_http_server(port)

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
