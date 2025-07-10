"""
Library to load HTTP structure field values
according to RFC9651 <https://www.rfc-editor.org/rfc/rfc9651.html>
"""

from collections.abc import Callable, Iterable

from . import dump_primitives, load_primitives
from .exceptions import DumpError, LoadError, _ContinueLoading
from .reader import Reader
from .types import BareItem, Item, ItemList, Key


def _wrap_load[T](load_func: Callable[[Reader], T], data: str, strict: bool) -> T:
    try:
        data = data.encode("utf-8").decode("ascii")
    except ValueError as e:
        raise LoadError(str(e)) from e

    reader = Reader(data)
    load_primitives.discard_whitespaces(reader)

    try:
        result = load_func(reader)
    except _ContinueLoading:
        raise reader.load_error()

    if strict:
        load_primitives.discard_whitespaces(reader)
        if reader:
            raise reader.load_error("expected end of input")

    return result


def load_item(data: str, strict: bool = True) -> Item:
    "Load data as an HTTP structured item, raise LoadError in case of invalid input"
    return _wrap_load(load_primitives.load_item, data, strict)


def load_simple_item(data: str, strict: bool = True) -> BareItem:
    bare_item, _ = load_item(data, strict=strict)
    return bare_item


def load_list(data: str, strict: bool = True) -> list[Item | ItemList]:
    "Load data as an HTTP structured list, raise LoadError in case of invalid input"
    return _wrap_load(load_primitives.load_list, data, strict)


def load_simple_list(data: str, strict: bool = True) -> list[BareItem | list[BareItem]]:
    return [
        [v for v, _ in item] if isinstance(item, list) else item
        for item, _ in load_list(data, strict=strict)
    ]


def load_dict(data: str, strict: bool = True) -> dict[Key, Item | ItemList]:
    "Load data as an HTTP structured dictionnary, raise LoadError in case of invalid input"
    return _wrap_load(load_primitives.load_dict, data, strict)


def load_simple_dict(data: str, strict: bool = True) -> dict[Key, BareItem | list[BareItem]]:
    return {
        key: [v for v, _ in item] if isinstance(item, list) else item
        for key, (item, _) in load_dict(data, strict=strict).items()
    }


def _wrap_dump[T](dump_func: Callable[[T], Iterable[str]], item: T) -> str:
    return "".join(dump_func(item))


def dump_item(item: Item | ItemList) -> str:
    "Dump a value item as an HTTP structured item, raise DumpError in case of invalid value"
    return _wrap_dump(dump_primitives.dump_item_or_inner_list, item)


def dump_simple_item(item: BareItem | list[BareItem]) -> str:
    if isinstance(item, list):
        item = [(v, {}) for v in item]
    return dump_item((item, {}))


def dump_list(items: list[Item | ItemList]) -> str:
    "Dump a list as an HTTP structured list, raise DumpError in case of invalid value"
    return _wrap_dump(dump_primitives.dump_list, items)


def dump_simple_list(items: list[BareItem | list[BareItem]]) -> str:
    return dump_list([
        (
            [(v, {}) for v in item] if isinstance(item, list) else item,
            {},
        )
        for item in items
    ])


def dump_dict(items: dict[str | Key, Item | ItemList]) -> str:
    "Dump a dict as an HTTP structured dictionnary, raise DumpError in case of invalid value"
    return _wrap_dump(dump_primitives.dump_dict, items)


def dump_simple_dict(items: dict[str | Key, BareItem | list[BareItem]]) -> str:
    return dump_dict({
        key: (
            [(v, {}) for v in item] if isinstance(item, list) else item,
            {},
        )
        for key, item in items.items()
    })


__all__ = [
    "DumpError",
    "LoadError",
    "dump_dict",
    "dump_item",
    "dump_list",
    "dump_simple_dict",
    "dump_simple_item",
    "dump_simple_list",
    "load_dict",
    "load_item",
    "load_list",
    "load_simple_dict",
    "load_simple_item",
    "load_simple_list",
]
