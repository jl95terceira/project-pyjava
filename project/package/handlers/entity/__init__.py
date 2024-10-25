from ... import model

import abc
from   dataclasses import dataclass, field

@dataclass
class PackageDeclaration:

    name:str = field()

@dataclass
class ImportDeclaration: 

    name  :str  = field()
    static:bool = field(default=False)

@dataclass
class ClassHeaderDeclaration:

    name  :str               = field()
    header:model.ClassHeader = field()
    static:bool              = field(default=False)

@dataclass
class InitializerDeclaration:

    initializer:model.Initializer = field()
    static     :bool              = field(default=False)

@dataclass
class ConstructorDeclaration:

    constructor:model.Constructor = field()

@dataclass
class AttributeDeclaration:

    name     :str             = field()
    attribute:model.Attribute = field()
    static   :bool            = field(default=False)

@dataclass
class MethodDeclaration:

    name  :str          = field()
    method:model.Method = field()
    static:bool         = field(default=False)

@dataclass
class EnumValueDeclaration:

    name     :str             = field()
    enumvalue:model.EnumValue = field()

class Handler(abc.ABC):

    @abc.abstractmethod
    def handle_package      (self, package      :PackageDeclaration):  ...
    @abc.abstractmethod
    def handle_import       (self, import_      :ImportDeclaration):  ...
    @abc.abstractmethod
    def handle_class        (self, class_       :ClassHeaderDeclaration):  ...
    @abc.abstractmethod
    def handle_class_end    (self):  ...
    @abc.abstractmethod
    def handle_initializer  (self, initializer  :InitializerDeclaration):  ...
    @abc.abstractmethod
    def handle_constructor  (self, constructor  :ConstructorDeclaration):  ...
    @abc.abstractmethod
    def handle_attribute    (self, attribute    :AttributeDeclaration):  ...
    @abc.abstractmethod
    def handle_method       (self, method       :MethodDeclaration):  ...
    @abc.abstractmethod
    def handle_enum_value   (self, enumvalue    :EnumValueDeclaration):  ...
    @abc.abstractmethod
    def handle_comment      (self, comment      :model.Comment): ...

from .builder import Builder
