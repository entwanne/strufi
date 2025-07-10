import base64
import math
from collections.abc import Generator
from datetime import datetime
from typing import cast

from .exceptions import DumpError
from .load_primitives import KEY_CHARS, KEY_START_CHARS, STRING_CHARS, TOKEN_START_CHARS, TOKEN_CHARS
from .types import BareItem, Item, ItemList, Parameters, SimpleString, Token, DisplayString


def dump_integer(value: int) -> Generator[str]:
    if not -(10**15) < value < 10**15:
        raise DumpError(f"Integer {value!r} is out of bounds")
    yield str(value)


def dump_decimal(value: float) -> Generator[str]:
    if math.isnan(value) or not -(10**12) < value < 10**12:
        raise DumpError(f"Decimal {value!r} is out of bounds")
    data = format(value, ".3f").rstrip("0")
    yield data
    if data.endswith("."):
        yield "0"


def _check_simple_string(value: str) -> bool:
    try:
        value.encode("ascii").decode("utf-8")
    except ValueError:
        return False

    if any(c not in STRING_CHARS for c in value):
        return False

    return True


def dump_simple_string(value: str, check: bool = True) -> Generator[str]:
    if check and not _check_simple_string(value):
        raise DumpError("Non-ascii or non-printable characters are not allowed in simple strings")

    yield '"'

    for char in value:
        if char in '"\\':
            yield "\\"
        yield char

    yield '"'


def dump_token(value: str) -> Generator[str]:
    if not value:
        raise DumpError("Token cannot be empty")
    if value[0] not in TOKEN_START_CHARS:
        raise DumpError(f"Token must start with letter or '*', not {value[0]!r}")
    for char in value[1:]:
        if char not in TOKEN_CHARS:
            raise DumpError(f"Token cannot contain character {char!r}")

    yield value


def dump_display_string(value: str) -> Generator[str]:
    raw_data = value.encode("utf-8")
    yield '%"'

    for byte in raw_data:
        char = chr(byte)
        if char not in STRING_CHARS or char in {'"', "%"}:
            yield f"%{byte:02x}"
        else:
            yield char

    yield '"'


def dump_string(value: str) -> Generator[str]:
    if _check_simple_string(value):
        return dump_simple_string(value, check=False)
    else:
        return dump_display_string(value)


def dump_bytes(value: bytes) -> Generator[str]:
    yield ":"
    yield base64.b64encode(value).decode("utf-8")
    yield ":"


def dump_boolean(value: bool) -> Generator[str]:
    if value:
        yield "?1"
    else:
        yield "?0"


def dump_date(value: datetime) -> Generator[str]:
    if value.tzinfo is None:
        raise DumpError("Cannot dump naive datetime object")

    yield "@"
    yield str(int(value.timestamp()))


def dump_bare_item(value: BareItem) -> Generator[str]:
    match value:
        case bool():
            return dump_boolean(value)
        case int():
            return dump_integer(value)
        case float():
            return dump_decimal(value)
        case Token():
            return dump_token(value)
        case SimpleString():
            return dump_simple_string(value)
        case DisplayString():
            return dump_display_string(value)
        case str():
            return dump_string(value)
        case bytes():
            return dump_bytes(value)
        case datetime():
            return dump_date(value)


def dump_key(key: str) -> Generator[str]:
    if not key:
        raise DumpError("Key cannot ben empty")
    if key[0] not in KEY_START_CHARS:
        raise DumpError(f"Key must start with lowercase letter or '*', not {key[0]!r}")
    for char in key[1:]:
        if char not in KEY_CHARS:
            raise DumpError(
                f"Key must contain only lowercase letters, digits, '*', '_', '-' or '.', not {char!r}"
            )

    yield key


def dump_parameters(parameters: Parameters) -> Generator[str]:
    for key, value in parameters.items():
        yield ";"
        yield from dump_key(key)
        if value is not True:
            yield "="
            yield from dump_bare_item(value)


def dump_item(item: Item) -> Generator[str]:
    (value, parameters) = item
    yield from dump_bare_item(value)
    yield from dump_parameters(parameters)


def dump_inner_list(item_list: ItemList) -> Generator[str]:
    (items, parameters) = item_list
    yield "("

    for i, item in enumerate(items):
        if i:
            yield " "
        yield from dump_item(item)

    yield ")"
    yield from dump_parameters(parameters)


def dump_item_or_inner_list(item: Item | ItemList) -> Generator[str]:
    (value, _) = item

    if isinstance(value, list):
        return dump_inner_list(cast(ItemList, item))
    else:
        return dump_item(cast(Item, item))


def dump_list(items: list[Item | ItemList]) -> Generator[str]:
    for i, item in enumerate(items):
        if i:
            yield ", "
        yield from dump_item_or_inner_list(item)


def dump_dict(items: dict[str, Item | ItemList]) -> Generator[str]:
    for i, (key, item) in enumerate(items.items()):
        if i:
            yield ", "
        yield from dump_key(key)

        value, parameters = item
        if value is True:
            yield from dump_parameters(parameters)
        else:
            yield "="
            yield from dump_item_or_inner_list(item)
