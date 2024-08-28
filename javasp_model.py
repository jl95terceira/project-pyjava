import dataclasses

import batteries
import javasp_words as words

@dataclasses.dataclass(frozen=True)
class AccessModifier:

    name:str

class AccessModifiers:

    _e:batteries.Enumerator[AccessModifier] = batteries.Enumerator()
    PUBLIC          = _e.E(AccessModifier(name=words.reserved('public')))
    PROTECTED       = _e.E(AccessModifier(name=words.reserved('protected')))
    PACKAGE_PRIVATE = _e.E(AccessModifier(name=''))
    PRIVATE         = _e.E(AccessModifier(name=words.reserved('private')))
    @staticmethod
    def values(): yield from AccessModifiers._e

@dataclasses.dataclass
class Argument:

    name     :str
    type_name:str
