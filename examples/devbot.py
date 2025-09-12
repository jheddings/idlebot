"""Basic IRC bot for testing our IRC client."""

import datetime
import logging
import time

from idlebot import irc

logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)s] (%(threadName)s) %(message)s"
)

logger = logging.getLogger("PyBot")


def on_welcome(client, msg):
    logger.info("Connection registered -- %s", msg)
    client.join("#pybot")


def on_connect(client):
    logger.info("Connected to server")


def on_privmsg(client, sender, recip, msg):
    logger.info("Message Received: %s => %s -- %s", sender, recip, msg)

    if recip.startswith("#"):
        client.msg(recip, f"echo -- {msg}")
    else:
        client.msg(sender, f"echo -- {msg}")


def on_join(client, channel):
    logger.info("Client joined channel: %s", channel)
    client.msg(channel, f"Hello World - {datetime.datetime.now()}")


def on_part(client, channel, msg):
    if msg is None:
        logger.info("Client left channel: %s", channel)
    else:
        logger.info("Client left channel: %s -- %s", channel, msg)


def on_quit(client, msg):
    if msg is None:
        logger.info("Disconnected from server")
    else:
        logger.info("Disconnected from server -- %s", msg)


## configure the client and event handlers
client = irc.Client("pybot", "PyBot")

client.on_connect += on_connect
client.on_welcome += on_welcome
client.on_join += on_join
client.on_part += on_part
client.on_privmsg += on_privmsg
client.on_quit += on_quit

## connect to the IRC server
client.connect("localhost")

# wait for user to quit (Ctrl-C)
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("anceled by user")

client.part("#pybot", "PyBot Terminating")
client.quit()
