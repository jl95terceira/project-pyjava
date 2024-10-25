import typing

from .   import part, entity, expr, name, package, import_, body, callargs, generics, signature, type, annotation
from ..  import model, handlers

class StreamPrinter(handlers.entity.Handler):

    @typing.override
    def handle_package    (self, package:handlers.entity.PackageDeclaration):

        print(f'Handling package:               {package}')

    @typing.override
    def handle_import     (self, import_:handlers.entity.ImportDeclaration):

        print(f'Handling import:                {import_}')

    @typing.override
    def handle_class      (self, class_:handlers.entity.ClassHeaderDeclaration):

        print(f'Handling class:                 {class_}')

    @typing.override
    def handle_class_end  (self):

        print(f'Handling end of class')

    @typing.override
    def handle_initializer(self, initializer:handlers.entity.InitializerDeclaration):

        print(F'Handling initializer:           {initializer}')

    @typing.override
    def handle_constructor(self, constructor:handlers.entity.ConstructorDeclaration):

        print(f'Handling constructor:           {constructor}')

    @typing.override
    def handle_attribute  (self, attribute:handlers.entity.AttributeDeclaration):

        print(f'Handling attribute:             {attribute}')

    @typing.override
    def handle_method     (self, method:handlers.entity.MethodDeclaration):

        print(f'Handling method:                {method}')

    @typing.override
    def handle_enum_value (self, enumvalue:handlers.entity.EnumValueDeclaration):

        print(f'Handling enum value:            {enumvalue}')

    @typing.override
    def handle_comment    (self, comment:model.Comment):

        print(f'Handling comment:               {comment}')

class SilentHandler(handlers.entity.Handler):

    @typing.override
    def handle_package    (self, package    :handlers.entity.PackageDeclaration): pass
    @typing.override
    def handle_import     (self, import_    :handlers.entity.ImportDeclaration): pass
    @typing.override
    def handle_class      (self, class_     :handlers.entity.ClassHeaderDeclaration): pass
    @typing.override
    def handle_class_end  (self): pass
    @typing.override
    def handle_initializer(self, initializer:handlers.entity.InitializerDeclaration): pass
    @typing.override
    def handle_constructor(self, constructor:handlers.entity.ConstructorDeclaration): pass
    @typing.override
    def handle_attribute  (self, attribute  :handlers.entity.AttributeDeclaration): pass
    @typing.override
    def handle_method     (self, method     :handlers.entity.MethodDeclaration): pass
    @typing.override
    def handle_enum_value (self, enumvalue  :handlers.entity.EnumValueDeclaration): pass
    @typing.override
    def handle_comment    (self, comment    :model.Comment): pass
