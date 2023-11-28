"""Metrics provider for idlebot."""

from prometheus_client import Counter, Gauge

PLAYER_STATUS = Gauge(
    "idlerpg_status",
    "The status of the current player.",
    labelnames=["player"],
)

PLAYER_LEVEL = Gauge(
    "idlerpg_player_level",
    "The current level of a player.",
    labelnames=["player"],
)

NEXT_LEVEL = Counter(
    "idlerpg_next_level",
    "Time until player reaches the next level (in seconds).",
    labelnames=["player"],
)


class AppMetrics:
    def __init__(self, bot):
        self._bot = bot

        self.status = PLAYER_STATUS.labels(player=bot.rpg_username)
        self.current_level = PLAYER_LEVEL.labels(player=bot.rpg_username)
        self.next_level = PLAYER_LEVEL.labels(player=bot.rpg_username)
