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
    def handle_initializer  (self, initializer  :model.Initializer):  ...
    @abc.abstractmethod
    def handle_constructor  (self, constructor  :model.Constructor):  ...
    @abc.abstractmethod
    def handle_attr         (self, attribute    :model.Attribute):  ...
    @abc.abstractmethod
    def handle_method       (self, method       :model.Method):  ...
    @abc.abstractmethod
    def handle_enum_value   (self, enum         :model.EnumValue):  ...
    @abc.abstractmethod
    def handle_comment      (self, comment      :model.Comment): ...

from ._builder import Builder
