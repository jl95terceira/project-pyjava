import dataclasses
import typing

from . import handlers

@dataclasses.dataclass(frozen=True)
class Named:

    name:str
