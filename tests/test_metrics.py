import logging
import unittest

from idlebot.metrics import NEXT_LEVEL, PLAYER_LEVEL, PLAYER_STATUS, PlayerMetrics
from idlebot.player import PlayerInfo

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class PlayerMetricsTest(unittest.TestCase):
    def _load_player(self):
        with open("tests/player.xml") as fp:
            return PlayerInfo.from_xml(fp.read())

    def test_update_from_status(self):
        player = self._load_player()

        metrics = PlayerMetrics(player.username)
        metrics.update(player)

        labels = {"player": player.username}

        # fixture: level 13, ttl 3189, offline
        self.assertEqual(PLAYER_STATUS.labels(**labels)._value.get(), 0)
        self.assertEqual(PLAYER_LEVEL.labels(**labels)._value.get(), 13)
        self.assertEqual(NEXT_LEVEL.labels(**labels)._value.get(), 3189)

    def test_online_status(self):
        player = self._load_player()
        player.is_online = True

        metrics = PlayerMetrics(player.username)
        metrics.update(player)

        status = PLAYER_STATUS.labels(player=player.username)
        self.assertEqual(status._value.get(), 1)
