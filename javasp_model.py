import dataclasses

import batteries

@dataclasses.dataclass(frozen=True)
class AccessModifier:

    name:str

class AccessModifiers:

    _e:batteries.Enumerator[AccessModifier] = batteries.Enumerator()
    PUBLIC          = _e.E(AccessModifier(name='public'))
    PROTECTED       = _e.E(AccessModifier(name='protected'))
    PACKAGE_PRIVATE = _e.E(AccessModifier(name=''))
    PRIVATE         = _e.E(AccessModifier(name='private'))
    @staticmethod
    def values(): yield from AccessModifiers._e
