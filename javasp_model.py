import dataclasses

import javasp_words as words
import javasp_util  as util
from batteries import *

class ClassType(util.Named): pass
class ClassTypes:

    _e:Enumerator[ClassType] = Enumerator()
    CLASS     = _e(ClassType(words.CLASS))
    INTERFACE = _e(ClassType(words.INTERFACE))
    @staticmethod
    def values(): yield from ClassTypes._e

class FinalityType(util.Named): pass
class FinalityTypes:

    _e:Enumerator[FinalityType] = Enumerator()
    DEFAULT         = _e(FinalityType(''))
    ABSTRACT        = _e(FinalityType(words.ABSTRACT))
    FINAL           = _e(FinalityType(words.FINAL))
    def values(): yield from FinalityTypes._e

class AccessModifier(util.Named): pass
class AccessModifiers:

    _e:Enumerator[AccessModifier] = Enumerator()
    PUBLIC          = _e(AccessModifier(words.PUBLIC))
    PROTECTED       = _e(AccessModifier(words.PROTECTED))
    PACKAGE_PRIVATE = _e(AccessModifier(''))
    PRIVATE         = _e(AccessModifier(words.PRIVATE))
    @staticmethod
    def values(): yield from AccessModifiers._e

@dataclasses.dataclass
class Argument:

    type_name:str
    final    :bool
