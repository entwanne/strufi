from datetime import datetime
from typing import TypeAlias


class SimpleString(str):
    pass


class Token(str):
    pass


class DisplayString(str):
    pass


class Key(str):
    pass


BareItem: TypeAlias = bool | int | float | str | bytes | datetime | SimpleString | Token | DisplayString
Parameters: TypeAlias = dict[str | Key, BareItem]
Item: TypeAlias = tuple[BareItem, Parameters]
ItemList: TypeAlias = tuple[list[Item], Parameters]
