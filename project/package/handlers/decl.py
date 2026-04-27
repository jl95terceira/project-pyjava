from .. import model as _model

import dataclasses as _dc

@_dc.dataclass
class PackageDeclaration:

    name:str = _dc.field()

@_dc.dataclass
class ImportDeclaration: 

    name  :str  = _dc.field()
    static:bool = _dc.field(default=False)

@_dc.dataclass
class ClassHeaderDeclaration:

    name  :str               = _dc.field()
    header:_model.ClassHeader = _dc.field()
    static:bool              = _dc.field(default=False)

@_dc.dataclass
class InitializerDeclaration:

    initializer:_model.Initializer = _dc.field()
    static     :bool              = _dc.field(default=False)

@_dc.dataclass
class ConstructorDeclaration:

    constructor:_model.Constructor = _dc.field()

@_dc.dataclass
class AttributeDeclaration:

    name     :str             = _dc.field()
    attribute:_model.Attribute = _dc.field()
    static   :bool            = _dc.field(default=False)

@_dc.dataclass
class MethodDeclaration:

    name  :str          = _dc.field()
    method:_model.Method = _dc.field()
    static:bool         = _dc.field(default=False)

@_dc.dataclass
class EnumValueDeclaration:

    name     :str             = _dc.field()
    enumvalue:_model.EnumValue = _dc.field()
