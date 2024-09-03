import collections.abc
import dataclasses

from .batteries import *

from .          import words

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

@dataclasses.dataclass
class Package:

    name:str

@dataclasses.dataclass
class Import:

    name  :str
    static:bool

@dataclasses.dataclass
class Annotation:

    name:str

@dataclasses.dataclass
class Class:

    name      :str
    static    :bool
    access    :AccessModifier
    finality  :FinalityType
    type      :ClassType
    extends   :str|None
    implements:list[str]

@dataclasses.dataclass
class StaticConstructor:

    body:str

@dataclasses.dataclass
class Constructor:

    args:dict[str,Argument]
    body:str

@dataclasses.dataclass
class Attribute:

    name:str
    static:bool
    access:AccessModifier
    final:bool
    type_name:str
    value:str|None

@dataclasses.dataclass
class Method:

    name:str
    static:bool
    access:AccessModifier
    finality:FinalityType
    type_name:str
    args:dict[str,Argument]
    body:str|None

@dataclasses.dataclass
class EnumValue:

    name:str
    arg_values:list[str]


