import dataclasses

@dataclasses.dataclass(frozen=True)
class Named:

    name:str|None
