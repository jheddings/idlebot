"""Metrics wrapper for idlebot."""

from prometheus_client import Gauge

from .player import PlayerInfo

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

NEXT_LEVEL = Gauge(
    "idlerpg_next_level",
    "Time until player reaches the next level (in seconds).",
    labelnames=["player"],
)


class PlayerMetrics:
    def __init__(self, username: str):
        self.status = PLAYER_STATUS.labels(player=username)
        self.current_level = PLAYER_LEVEL.labels(player=username)
        self.next_level = NEXT_LEVEL.labels(player=username)

    def update(self, info: PlayerInfo):
        """Update all player metrics from the given status."""
        self.status.set(1 if info.is_online else 0)

        if info.level is not None:
            self.current_level.set(info.level)

        if info.ttl is not None:
            self.next_level.set(info.ttl.total_seconds())
