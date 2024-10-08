"""An IRC bot for playing IdleRPG."""

import logging
import signal

import click
from prometheus_client import start_http_server

from . import idlerpg, version
from .config import AppConfig
from .player import PlayerInfo

logger = logging.getLogger(__name__)


class MainApp:
    """Context used during main execution."""

    def __init__(self, config: AppConfig):
        self.logger = logger.getChild("MainApp")

        self.config = config

        self.bot = idlerpg.IdleBot(self.config)

    def _initialize_metrics(self, port=None):
        if port is None:
            self.logger.debug("metrics server disabled by config")
        else:
            self.logger.info("Initializing app metrics: %d", port)
            start_http_server(port)

    def __call__(self):
        self._initialize_metrics(self.config.metrics)

        self.bot.start()

        try:
            signal.pause()
        except KeyboardInterrupt:
            self.logger.debug("canceled by user")

        self.bot.stop()


@click.group()
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
@click.pass_context
def main(ctx, config):
    cfg = AppConfig.load(config)
    ctx.obj = MainApp(cfg)


@main.command("run")
@click.pass_obj
def do_run(app: MainApp):
    app()


@main.command("status")
@click.pass_obj
def do_status(app: MainApp):
    info = PlayerInfo.get(app.config.player.name)

    click.echo(f"You are {info.username}, the level {info.level} {info.character}")
    click.echo(f"Next level: {info.ttl} [{'online' if info.is_online else 'offline'}]")


@main.command("healthz")
@click.pass_obj
def do_healthz(app: MainApp):
    uname = app.config.player.name

    app.logger.debug("healthz check: %s", uname)
    info = PlayerInfo.get(uname)

    if not info.is_online:
        raise click.ClickException("Player is offline")

    click.echo("Player is online")


## MAIN ENTRY
if __name__ == "__main__":
    main()
