"""Player class for IdleBot."""


from datetime import timedelta
from enum import Enum

import requests
from pydantic_xml import BaseXmlModel, element


class Alignment(str, Enum):
    NEUTRAL = "n"
    GOOD = "g"
    EVIL = "e"


class PlayerInfo(BaseXmlModel, tag="player"):
    username: str = element()
    character: str = element(tag="class")
    alignment: Alignment = element(default=Alignment.NEUTRAL)

    level: int = element()
    ttl: timedelta = element()

    is_admin: bool = element(default=False, tag="isadmin")
    online: bool = element(default=False)

    @property
    def xml(self):
        return f"http://www.idlerpg.net/xml.php?player={self.username}"

    @property
    def profile(self):
        return f"http://www.idlerpg.net/playerview.php?player={self.username}"

    def update(self):
        pass

    @classmethod
    def get(cls, username: str):
        xml = f"http://www.idlerpg.net/xml.php?player={username}"
        resp = requests.get(xml)
        return cls.from_xml(resp.content)
