"""Player class for IdleBot."""

import xml.etree.ElementTree as ET
from enum import Enum
from typing import Optional

import requests
from pydantic_xml import BaseXmlModel, element


class Alignment(str, Enum):
    NEUTRAL = "n"
    GOOD = "g"
    EVIL = "e"


class PlayerInfo(BaseXmlModel, tag="player", search_mode="unordered"):
    username: str = element()
    character: str = element(tag="class")
    alignment: Alignment = element(default=Alignment.NEUTRAL)

    is_admin: bool = element(default=True, tag="isadmin")
    online: bool = element(default=False)

    level: Optional[int] = element(default=None)
    ttl: Optional[int] = element(default=None)

    @property
    def xml(self):
        return f"http://www.idlerpg.net/xml.php?player={self.username}"

    @property
    def profile(self):
        return f"http://www.idlerpg.net/playerview.php?player={self.username}"

    @classmethod
    def get(cls, username: str):
        xml = f"http://www.idlerpg.net/xml.php?player={username}"
        resp = requests.get(xml)
        tree = ET.fromstring(resp.content)
        return cls.from_xml_tree(tree)
