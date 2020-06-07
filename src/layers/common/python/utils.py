from dataclasses import fields
from typing import TypeVar, Type

T = TypeVar('T')


def dataclass_from_dict(dataclass: Type[T], d: dict) -> T:
    try:
        fieldtypes = {f.name: f.type for f in fields(dataclass)}
        return dataclass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except TypeError as e:
        if str(e) == "must be called with a dataclass type or instance":
            return d
        raise
