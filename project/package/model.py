import collections.abc
import dataclasses

from .batteries import *

from .          import words

@dataclasses.dataclass(frozen=True)
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

@dataclasses.dataclass(frozen=True)
class Argument:

    type_name:str  = dataclasses.field()
    final    :bool = dataclasses.field(default=False)

@dataclasses.dataclass(frozen=True)
class Package:

    name:str = dataclasses.field()

@dataclasses.dataclass(frozen=True)
class Import:

    name  :str  = dataclasses.field()
    static:bool = dataclasses.field(default=False)

@dataclasses.dataclass(frozen=True)
class Annotation:

    name:str

@dataclasses.dataclass(frozen=True)
class Class:

    name      :str
    type      :ClassType      = dataclasses.field(default=ClassTypes     .CLASS)
    static    :bool           = dataclasses.field(default=False)
    access    :AccessModifier = dataclasses.field(default=AccessModifiers.DEFAULT)
    finality  :FinalityType   = dataclasses.field(default=FinalityTypes  .DEFAULT)
    extends   :str|None       = dataclasses.field(default=None)
    implements:set[str]       = dataclasses.field(default_factory=set)

@dataclasses.dataclass(frozen=True)
class ClassEnd: pass

@dataclasses.dataclass(frozen=True)
class StaticConstructor:

    body:str

@dataclasses.dataclass(frozen=True)
class Constructor:

    args:dict[str,Argument]
    body:str

@dataclasses.dataclass(frozen=True)
class Attribute:

    name     :str
    type_name:str
    static   :bool           = dataclasses.field(default=False)
    access   :AccessModifier = dataclasses.field(default=AccessModifiers.DEFAULT)
    final    :bool           = dataclasses.field(default=False)
    value    :str|None       = dataclasses.field(default=None)

@dataclasses.dataclass(frozen=True)
class Method:

    name     :str                
    type_name:str
    static   :bool               = dataclasses.field(default=False)
    access   :AccessModifier     = dataclasses.field(default=AccessModifiers.DEFAULT)
    finality :FinalityType       = dataclasses.field(default=FinalityTypes  .DEFAULT)
    args     :dict[str,Argument] = dataclasses.field(default_factory=dict)
    body     :str|None           = dataclasses.field(default=None)

@dataclasses.dataclass(frozen=True)
class EnumValue:

    name      :str
    arg_values:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class Comment:

    text:str = dataclasses.field()
