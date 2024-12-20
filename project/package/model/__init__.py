import abc
from   collections import defaultdict
from   dataclasses import dataclass, field
import typing

from ..util import Named

from jl95terceira.batteries import Enumerator

class Entity(abc.ABC): pass

#    @abc.abstractmethod
#    def source(self): ...

@dataclass(frozen=True)
class ClassType(Named): pass
class ClassTypes:

    _e:Enumerator[ClassType] = Enumerator()
    CLASS      = _e(ClassType(name='CLASS'))
    INTERFACE  = _e(ClassType(name='INTERFACE'))
    ENUM       = _e(ClassType(name='ENUM'))
    AINTERFACE = _e(ClassType(name='@INTERFACE'))
    @staticmethod
    def values(): yield from ClassTypes._e

@dataclass(frozen=True)
class InheritanceType(Named): pass
class InheritanceTypes:

    _e:Enumerator[InheritanceType] = Enumerator()
    EXTENDS    = _e(InheritanceType(name='EXTENDS'))
    IMPLEMENTS = _e(InheritanceType(name='IMPLEMENTS'))
    @staticmethod
    def values(): yield from InheritanceTypes._e
    
@dataclass(frozen=True)
class FinalityType(Named): pass
class FinalityTypes:

    _e:Enumerator[FinalityType] = Enumerator()
    DEFAULT  = _e(FinalityType(name='DEFAULT'))
    ABSTRACT = _e(FinalityType(name='ABSTRACT'))
    FINAL    = _e(FinalityType(name='FINAL'))
    def values(): yield from FinalityTypes._e

@dataclass(frozen=True)
class AccessModifier(Named): pass
class AccessModifiers:

    _e:Enumerator[AccessModifier] = Enumerator()
    PUBLIC    = _e(AccessModifier(name='PUBLIC'))
    PROTECTED = _e(AccessModifier(name='PROTECTED'))
    DEFAULT   = _e(AccessModifier(name='DEFAULT'))
    PRIVATE   = _e(AccessModifier(name='PRIVATE'))
    @staticmethod
    def values(): yield from AccessModifiers._e

@dataclass
class Package: pass # sentinel

@dataclass
class Import: pass # sentinel

@dataclass
class Annotation:

    name:str       = field()
    args:list[str] = field(default_factory=list)

    @typing.override
    def source(self): return f'@{self.name}{'' if not self.args else f'({', '.join(self.args)})'}'

@dataclass
class Type:

    name       :str                      = field()
    generics   :list['GenericType']|None = field(default        =None)
    array_dim  :int                      = field(default        =0)
    annotations:list[Annotation]         = field(default_factory=list)

    @typing.override
    def source(self): return f'{self.name}{'' if self.generics is None else f'<{', '.join(map(lambda t: t.source(), self.generics))}>'}'

@dataclass(frozen=True)
class TypeConstraint(Named): pass
class TypeConstraints:

    _e:Enumerator[TypeConstraint] = Enumerator()
    NONE    = _e(TypeConstraint(name=None))
    EXTENDS = _e(TypeConstraint(name='EXTENDS'))
    SUPER   = _e(TypeConstraint(name='SUPER'))

    @typing.override
    def source(self): raise NotImplementedError()

@dataclass
class ConstrainedType:

    name      :str            = field()
    targets   :list[Type]     = field()
    constraint:TypeConstraint = field(default=TypeConstraints.NONE)

    @typing.override
    def source(self) : return f'{self.name}{'' if self.constraint is TypeConstraints.NONE else f' {self.constraint.source()} {' & '.join(target.source() for target in self.targets)}'}'

@dataclass
class UnboundedType: pass

GenericType = typing.Union[Type, ConstrainedType, UnboundedType]

@dataclass
class ConcreteClassHeader:

    annotations:list[Annotation]                 = field(default_factory=list)
    generics   :list[GenericType]|None           = field(default        =None)
    access     :AccessModifier                   = field(default        =AccessModifiers.DEFAULT)
    finality   :FinalityType                     = field(default        =FinalityTypes  .DEFAULT)
    inherit    :dict[InheritanceType,list[Type]] = field(default_factory=lambda: defaultdict(list))
    signature  :dict[str, 'Argument']|None       = field(default        =None)

@dataclass
class AbstractClassHeader:

    annotations:list[Annotation]                 = field(default_factory=list)
    generics   :list[GenericType]|None           = field(default        =None)
    access     :AccessModifier                   = field(default        =AccessModifiers.DEFAULT)
    inherit    :dict[InheritanceType,list[Type]] = field(default_factory=lambda: defaultdict(list))

@dataclass
class InterfaceHeader:

    annotations:list[Annotation]                 = field(default_factory=list)
    generics   :list[GenericType]|None           = field(default        =None)
    access     :AccessModifier                   = field(default        =AccessModifiers.DEFAULT)
    inherit    :list[Type]                       = field(default_factory=list)

ClassHeader = typing.Union[ConcreteClassHeader, AbstractClassHeader, InterfaceHeader]

@dataclass
class AInterface:

    name       :str              = field()
    annotations:list[Annotation] = field(default_factory=list)
    access     :AccessModifier   = field(default        =AccessModifiers.DEFAULT)

@dataclass
class Argument:

    type       :Type             = field()
    final      :bool             = field(default        =False)
    varargs    :bool             = field(default        =False)
    annotations:list[Annotation] = field(default_factory=list)

@dataclass
class Initializer:

    body:str = field()

@dataclass
class Constructor:

    body  :str                = field()
    args  :dict[str,Argument] = field(default_factory=dict)
    access:AccessModifier     = field(default        =AccessModifiers.DEFAULT)
    throws:list[Type]         = field(default_factory=list)

@dataclass
class Attribute:

    type     :Type           = field()
    volatile :bool           = field(default=False)
    access   :AccessModifier = field(default=AccessModifiers.DEFAULT)
    final    :bool           = field(default=False)
    transient:bool           = field(default=False)
    value    :str|None       = field(default=None)

@dataclass
class ConcreteMethod:

    type         :Type              |None = field()
    access       :AccessModifier          = field(default        =AccessModifiers.DEFAULT)
    finality     :FinalityType            = field(default        =FinalityTypes  .DEFAULT)
    synchronized :bool                    = field(default        =False)
    generics     :list[GenericType] |None = field(default        =None)
    args         :dict[str,Argument]      = field(default_factory=dict)
    throws       :list[Type]              = field(default_factory=list)
    body         :str                     = field(default        ='')

@dataclass
class InterfaceMethod:

    type         :Type              |None = field()
    default      :bool                    = field(default        =False)
    generics     :list[GenericType] |None = field(default        =None)
    args         :dict[str,Argument]      = field(default_factory=dict)
    throws       :list[Type]              = field(default_factory=list)
    default_value:str               |None = field(default        =None)

@dataclass
class AbstractMethod:

    type         :Type              |None = field()
    access       :AccessModifier          = field(default        =AccessModifiers.DEFAULT)
    synchronized :bool                    = field(default        =False)
    generics     :list[GenericType] |None = field(default        =None)
    args         :dict[str,Argument]      = field(default_factory=dict)
    throws       :list[Type]              = field(default_factory=list)

Method = typing.Union[ConcreteMethod, InterfaceMethod, AbstractMethod]

@dataclass
class EnumValue:

    annotations:list[Annotation]           = field(default_factory=list)
    args       :list[str]                  = field(default_factory=list)
    subclass   :typing.Union['Class',None] = field(default        =None)

@dataclass
class Comment:

    text:str = field()

@dataclass
class StaticMembers:

    attributes :dict[str,list[Attribute]]      = field(default_factory=lambda: defaultdict(list))
    initializer:Initializer              |None = field(default        =None)
    methods    :dict[str,list[ConcreteMethod]] = field(default_factory=lambda: defaultdict(list))
    classes    :dict[str,'Class']              = field(default_factory=dict)

@dataclass
class Members:

    attributes        :dict[str,Attribute]         = field(default_factory=dict)
    initializer       :Initializer           |None = field(default        =None)
    constructors      :list[Constructor]           = field(default_factory=list)
    methods           :dict[str,list[Method]]      = field(default_factory=lambda: defaultdict(list))
    classes           :dict[str,'Class']           = field(default_factory=dict)
    enumvalues        :dict[str,EnumValue]         = field(default_factory=dict)

@dataclass
class ConcreteClass:

    header        :ConcreteClassHeader = field()
    static_members:StaticMembers       = field(kw_only=True, default_factory=StaticMembers)
    members       :Members             = field(default_factory=Members)

@dataclass
class AbstractClass:

    header        :AbstractClassHeader = field()
    static_members:StaticMembers       = field(kw_only=True, default_factory=StaticMembers)
    members       :Members             = field(default_factory=Members)

@dataclass
class Interface:

    header        :InterfaceHeader = field()
    static_members:StaticMembers   = field(kw_only=True, default_factory=StaticMembers)
    members       :Members         = field(default_factory=Members)

Class = typing.Union[ConcreteClass, AbstractClass, Interface]

@dataclass
class Unit:

    package       :str             |None = field(default        =None)
    imports       :dict[str,Import]      = field(default_factory=dict)
    imports_static:dict[str,Import]      = field(default_factory=dict)
    classes       :dict[str,Class]       = field(default_factory=dict)
