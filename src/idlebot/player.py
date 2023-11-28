"""Player class for IdleBot."""

from datetime import timedelta

from .metrics import PlayerMetrics


class Player:
    def __init__(self, name, password, class_):
        self.name = name
        self.password = password
        self.character = class_

        self._online = False
        self._level = None
        self._next_level = None

        self._metrics = PlayerMetrics(self)

    @property
    def online(self) -> bool:
        return self._online

    @online.setter
    def online(self, value: bool):
        self._online = value
        self._metrics.status.set(value)

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int):
        self._level = value

        if value is None:
            self._metrics.current_level.set(0)
        else:
            self._metrics.current_level.set(value)

    @property
    def next_level(self) -> timedelta:
        return self._next_level

    @next_level.setter
    def next_level(self, value: timedelta):
        self._next_level = value

        if value is None:
            self._metrics.next_level.set(0)
        else:
            self._metrics.next_level.set(value.total_seconds())
