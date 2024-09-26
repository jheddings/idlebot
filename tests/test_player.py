import logging
import unittest

from idlebot.player import PlayerInfo

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class PlayerInfoTest(unittest.TestCase):
    def test_player_xml(self):
        with open("tests/player.xml") as fp:
            text = fp.read()

        player = PlayerInfo.from_xml(text)

        self.assertEqual(player.username, "test_subject")
