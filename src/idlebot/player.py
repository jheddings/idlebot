"""Player class for IdleBot."""


from pydantic_xml import BaseXmlModel, element


class Player(BaseXmlModel, tag="player"):
    username: str = element()
    is_admin: bool = element(tag="isadmin")
    level: int = element()
    online: bool = element()
    ttl: int = element()
    clazz: int = element(tag="class")
