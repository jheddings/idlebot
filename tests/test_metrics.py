import logging
import unittest

from prometheus_client import REGISTRY

from idlebot.metrics import PlayerMetrics
from idlebot.player import PlayerInfo

# keep logging output to a minumim for testing
logging.basicConfig(level=logging.FATAL)


class PlayerMetricsTest(unittest.TestCase):
    def _load_player(self):
        with open("tests/player.xml") as fp:
            return PlayerInfo.from_xml(fp.read())

    def _sample(self, name, **labels):
        return REGISTRY.get_sample_value(name, labels)

    def test_update_from_status(self):
        player = self._load_player()

        metrics = PlayerMetrics(player.username)
        metrics.update(player)

        name = player.username

        # fixture: level 13, ttl 3189, offline
        self.assertEqual(self._sample("idlerpg_player_online", player=name), 0)
        self.assertEqual(self._sample("idlerpg_player_level", player=name), 13)
        self.assertEqual(self._sample("idlerpg_player_next_level_seconds", player=name), 3189)

    def test_online_status(self):
        player = self._load_player()
        player.is_online = True

        PlayerMetrics(player.username).update(player)

        self.assertEqual(self._sample("idlerpg_player_online", player=player.username), 1)

    def test_player_info(self):
        player = self._load_player()

        PlayerMetrics(player.username).update(player)

        # fixture: class "Human Trial", alignment neutral
        value = self._sample(
            "idlerpg_player_info",
            player=player.username,
            character=player.character,
            alignment=str(player.alignment),
        )
        self.assertEqual(value, 1)

    def test_last_update_recorded(self):
        player = self._load_player()

        PlayerMetrics(player.username).update(player)

        ts = self._sample("idlerpg_player_updated_timestamp_seconds", player=player.username)
        assert ts is not None
        self.assertGreater(ts, 0)
