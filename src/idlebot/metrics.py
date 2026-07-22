"""Metrics wrapper for idlebot."""

from prometheus_client import Gauge, Info

from .player import PlayerInfo

PLAYER_ONLINE = Gauge(
    "idlerpg_player_online",
    "Whether the player is currently online (1) or offline (0).",
    labelnames=["player"],
)

PLAYER_LEVEL = Gauge(
    "idlerpg_player_level",
    "The current level of a player.",
    labelnames=["player"],
)

NEXT_LEVEL = Gauge(
    "idlerpg_player_next_level_seconds",
    "Time until the player reaches the next level (in seconds).",
    labelnames=["player"],
)

LAST_UPDATE = Gauge(
    "idlerpg_player_updated_timestamp_seconds",
    "Unix timestamp of the last player status update.",
    labelnames=["player"],
)

PLAYER_INFO = Info(
    "idlerpg_player",
    "Static attributes of the player.",
    labelnames=["player"],
)


class PlayerMetrics:
    def __init__(self, username: str):
        self.online = PLAYER_ONLINE.labels(player=username)
        self.current_level = PLAYER_LEVEL.labels(player=username)
        self.next_level = NEXT_LEVEL.labels(player=username)
        self.last_update = LAST_UPDATE.labels(player=username)
        self.info = PLAYER_INFO.labels(player=username)

    def update(self, info: PlayerInfo):
        """Update all player metrics from the given status."""
        self.online.set(1 if info.is_online else 0)

        if info.level is not None:
            self.current_level.set(info.level)

        if info.ttl is not None:
            self.next_level.set(info.ttl.total_seconds())

        self.info.info(
            {
                "character": info.character,
                "alignment": str(info.alignment),
            }
        )

        self.last_update.set_to_current_time()
