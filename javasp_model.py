import dataclasses
import functools
import uuid

import javasp_words as words
from batteries import *

@dataclasses.dataclass
class HashedAndKeyworded:

    keyword:str = dataclasses.field()

class ClassType(HashedAndKeyworded): pass
class ClassTypes:

    _e:Enumerator[ClassType] = Enumerator()
    CLASS     = _e(ClassType(keyword=words.CLASS))
    INTERFACE = _e(ClassType(keyword=words.INTERFACE))
    ENUM      = _e(ClassType(keyword=words.ENUM))
    @staticmethod
    def values(): yield from ClassTypes._e

class FinalityType(HashedAndKeyworded): pass
class FinalityTypes:

    _e:Enumerator[FinalityType] = Enumerator()
    DEFAULT  = _e(FinalityType(keyword=''))
    ABSTRACT = _e(FinalityType(keyword=words.ABSTRACT))
    FINAL    = _e(FinalityType(keyword=words.FINAL))
    def values(): yield from FinalityTypes._e

class AccessModifier(HashedAndKeyworded): pass
class AccessModifiers:

    _e:Enumerator[AccessModifier] = Enumerator()
    PUBLIC    = _e(AccessModifier(keyword=words.PUBLIC))
    PROTECTED = _e(AccessModifier(keyword=words.PROTECTED))
    DEFAULT   = _e(AccessModifier(keyword=''))
    PRIVATE   = _e(AccessModifier(keyword=words.PRIVATE))
    @staticmethod
    def values(): yield from AccessModifiers._e

@dataclasses.dataclass
class Argument:

    type_name:str
    final    :bool
