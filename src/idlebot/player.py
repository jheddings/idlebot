"""Player class for IdleBot."""

import xml.etree.ElementTree as ET
from datetime import timedelta
from enum import Enum
from typing import Optional

import requests
from pydantic import field_validator
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
    ttl: Optional[timedelta] = element(default=None)

    @field_validator("ttl", mode="before")
    @classmethod
    def ttl_as_int(cls, raw: str) -> int:
        # the XML fields all come as strings...  pydantic will try to convert them
        # as timedelta objects, but the ttl field is really just an integer
        return int(raw)

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
