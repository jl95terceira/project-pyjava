from   collections import defaultdict
import dataclasses

from .batteries import Enumerator
from .util      import Named

class ClassType(Named): pass
class ClassTypes:

    _e:Enumerator[ClassType] = Enumerator()
    CLASS     = _e(ClassType(name='CLASS'    ))
    INTERFACE = _e(ClassType(name='INTERFACE'))
    ENUM      = _e(ClassType(name='ENUM'     ))
    @staticmethod
    def values(): yield from ClassTypes._e

class InheritanceType(Named): pass
class InheritanceTypes:

    _e:Enumerator[InheritanceType] = Enumerator()
    EXTENDS    = _e(InheritanceType(name='EXTENDS'))
    IMPLEMENTS = _e(InheritanceType(name='IMPLEMENTS'))
    @staticmethod
    def values(): yield from InheritanceTypes._e
    
class FinalityType(Named): pass
class FinalityTypes:

    _e:Enumerator[FinalityType] = Enumerator()
    DEFAULT  = _e(FinalityType(name='DEFAULT' ))
    ABSTRACT = _e(FinalityType(name='ABSTRACT'))
    FINAL    = _e(FinalityType(name='FINAL'   ))
    def values(): yield from FinalityTypes._e

class AccessModifier(Named): pass
class AccessModifiers:

    _e:Enumerator[AccessModifier] = Enumerator()
    PUBLIC    = _e(AccessModifier(name='PUBLIC'   ))
    PROTECTED = _e(AccessModifier(name='PROTECTED'))
    DEFAULT   = _e(AccessModifier(name='DEFAULT'  ))
    PRIVATE   = _e(AccessModifier(name='PRIVATE'  ))
    @staticmethod
    def values(): yield from AccessModifiers._e

@dataclasses.dataclass(frozen=True)
class Package:

    name:str = dataclasses.field()

@dataclasses.dataclass(frozen=True)
class Import:

    name  :str  = dataclasses.field()
    static:bool = dataclasses.field(default=False)

@dataclasses.dataclass(frozen=True)
class Annotation:

    name:str       = dataclasses.field()
    args:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class Type:

    name     :str = dataclasses.field()
    generics :str = dataclasses.field(default='')
    array_dim:int = dataclasses.field(default=False)

@dataclasses.dataclass(frozen=True)
class Class:

    name      :str
    generics  :str            = dataclasses.field(default='')
    type      :ClassType      = dataclasses.field(default=ClassTypes     .CLASS)
    static    :bool           = dataclasses.field(default=False)
    access    :AccessModifier = dataclasses.field(default=AccessModifiers.DEFAULT)
    finality  :FinalityType   = dataclasses.field(default=FinalityTypes  .DEFAULT)
    subclass  :dict[InheritanceType,set[Type]] \
                              = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(frozen=True)
class ClassEnd: pass

@dataclasses.dataclass(frozen=True)
class Argument:

    type      :Type            = dataclasses.field()
    final     :bool            = dataclasses.field(default=False)
    annotation:Annotation|None = dataclasses.field(default=None)

@dataclasses.dataclass(frozen=True)
class StaticConstructor:

    body:str = dataclasses.field()

@dataclasses.dataclass(frozen=True)
class Constructor:

    args  :dict[str,Argument] = dataclasses.field()
    body  :str                = dataclasses.field()
    access:AccessModifier     = dataclasses.field(default=AccessModifiers.DEFAULT)

@dataclasses.dataclass(frozen=True)
class Attribute:

    name     :str            = dataclasses.field()
    type     :Type           = dataclasses.field()
    static   :bool           = dataclasses.field(default=False)
    volatile :bool           = dataclasses.field(default=False)
    access   :AccessModifier = dataclasses.field(default=AccessModifiers.DEFAULT)
    final    :bool           = dataclasses.field(default=False)
    value    :str|None       = dataclasses.field(default=None)

@dataclasses.dataclass(frozen=True)
class Method:

    name        :str                = dataclasses.field()
    type        :Type               = dataclasses.field()
    static      :bool               = dataclasses.field(default        =False)
    access      :AccessModifier     = dataclasses.field(default        =AccessModifiers.DEFAULT)
    finality    :FinalityType       = dataclasses.field(default        =FinalityTypes  .DEFAULT)
    synchronized:bool               = dataclasses.field(default        =False)
    generics    :str                = dataclasses.field(default        ='')
    args        :dict[str,Argument] = dataclasses.field(default_factory=dict)
    throws      :list[Type]         = dataclasses.field(default_factory=list)
    body        :str|None           = dataclasses.field(default        =None)

@dataclasses.dataclass(frozen=True)
class EnumValue:

    name:str       = dataclasses.field()
    args:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(frozen=True)
class Comment:

    text:str = dataclasses.field()
