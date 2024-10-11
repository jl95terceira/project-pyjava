import abc
import dataclasses
import typing

from ..          import words
from ..batteries import Enumerator
from ..util      import Named

class ClassType(Named): pass
class ClassTypes:

    _e:Enumerator[ClassType] = Enumerator()
    CLASS     = _e(ClassType(name='CLASS'))
    INTERFACE = _e(ClassType(name='INTERFACE'))
    ENUM      = _e(ClassType(name='ENUM'))
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
    DEFAULT  = _e(FinalityType(name='DEFAULT'))
    ABSTRACT = _e(FinalityType(name='ABSTRACT'))
    FINAL    = _e(FinalityType(name='FINAL'))
    def values(): yield from FinalityTypes._e

class AccessModifier(Named): pass
class AccessModifiers:

    _e:Enumerator[AccessModifier] = Enumerator()
    PUBLIC    = _e(AccessModifier(name='PUBLIC'))
    PROTECTED = _e(AccessModifier(name='PROTECTED'))
    DEFAULT   = _e(AccessModifier(name='DEFAULT'))
    PRIVATE   = _e(AccessModifier(name='PRIVATE'))
    @staticmethod
    def values(): yield from AccessModifiers._e

@dataclasses.dataclass
class Package:

    name:str = dataclasses.field()

@dataclasses.dataclass
class Import:

    name  :str  = dataclasses.field()
    static:bool = dataclasses.field(default=False)

    @typing.override
    def source(self): return f'{words.IMPORT} {'' if not self.static else f'{words.STATIC} '}{self.name};'

@dataclasses.dataclass
class Annotation:

    name:str       = dataclasses.field()
    args:list[str] = dataclasses.field(default_factory=list)

    @typing.override
    def source(self): return f'@{self.name}{'' if not self.args else f'({', '.join(self.args)})'}'

GenericType = typing.Union['Type','ConstrainedType']

@dataclasses.dataclass
class Type:

    name     :str                    = dataclasses.field()
    generics :list[GenericType]|None = dataclasses.field(default=None)
    array_dim:int                    = dataclasses.field(default=0)

    @typing.override
    def source(self): return f'{self.name}{'' if self.generics is None else f'<{', '.join(map(lambda t: t.source(), self.generics))}>'}'

@dataclasses.dataclass(frozen=True)
class TypeConstraint(Named): pass
class TypeConstraints:

    _e:Enumerator[TypeConstraint] = Enumerator()
    NONE    = _e(TypeConstraint(name=None))
    EXTENDS = _e(TypeConstraint(name='EXTENDS'))
    SUPER   = _e(TypeConstraint(name='SUPER'))

@dataclasses.dataclass
class ConstrainedType:

    name      :str            = dataclasses.field()
    target    :Type           = dataclasses.field()
    constraint:TypeConstraint = dataclasses.field(default=TypeConstraints.NONE)

    @typing.override
    def source(self) : return f'{self.name}{'' if self.constraint is TypeConstraints.NONE else f' {self.constraint.source()} {self.target.source()}'}'

@dataclasses.dataclass
class Class:

    name      :str
    generics  :list[GenericType]|None = dataclasses.field(default        =None)
    type      :ClassType              = dataclasses.field(default        =ClassTypes     .CLASS)
    static    :bool                   = dataclasses.field(default        =False)
    access    :AccessModifier         = dataclasses.field(default        =AccessModifiers.DEFAULT)
    finality  :FinalityType           = dataclasses.field(default        =FinalityTypes  .DEFAULT)
    subclass  :dict[InheritanceType,list[Type]] \
                                      = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class ClassEnd: pass

@dataclasses.dataclass
class Argument:

    type      :Type            = dataclasses.field()
    final     :bool            = dataclasses.field(default=False)
    annotation:Annotation|None = dataclasses.field(default=None)

@dataclasses.dataclass
class StaticConstructor:

    body:str = dataclasses.field()

@dataclasses.dataclass
class Constructor:

    args  :dict[str,Argument] = dataclasses.field()
    body  :str                = dataclasses.field()
    access:AccessModifier     = dataclasses.field(default=AccessModifiers.DEFAULT)

@dataclasses.dataclass
class Attribute:

    name     :str            = dataclasses.field()
    type     :Type           = dataclasses.field()
    static   :bool           = dataclasses.field(default=False)
    volatile :bool           = dataclasses.field(default=False)
    access   :AccessModifier = dataclasses.field(default=AccessModifiers.DEFAULT)
    final    :bool           = dataclasses.field(default=False)
    value    :str|None       = dataclasses.field(default=None)

@dataclasses.dataclass
class Method:

    name        :str                    = dataclasses.field()
    type        :Type                   = dataclasses.field()
    static      :bool                   = dataclasses.field(default        =False)
    access      :AccessModifier         = dataclasses.field(default        =AccessModifiers.DEFAULT)
    finality    :FinalityType           = dataclasses.field(default        =FinalityTypes  .DEFAULT)
    synchronized:bool                   = dataclasses.field(default        =False)
    generics    :list[GenericType]|None = dataclasses.field(default        =None)
    args        :dict[str,Argument]     = dataclasses.field(default_factory=dict)
    throws      :list[Type]             = dataclasses.field(default_factory=list)
    body        :str|None               = dataclasses.field(default        =None)

@dataclasses.dataclass
class EnumValue:

    name:str       = dataclasses.field()
    args:list[str] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class Comment:

    text:str = dataclasses.field()
