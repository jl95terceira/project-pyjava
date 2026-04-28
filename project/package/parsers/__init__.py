import typing

from .   import part, entity, expr, name, package, import_, body, args, generics, signature, type, annotation
from ..  import model, handlers

class StreamPrinter(handlers.entity.Handler):

    def __init__(self, printer:typing.Callable[[str],None]=lambda a: print(a, end='')):

        self._print = printer

    @typing.override
    def handle_package    (self, package:handlers.decl.PackageDeclaration):

        self._print(f'Handling package:               {package}\n')

    @typing.override
    def handle_import     (self, import_:handlers.decl.ImportDeclaration):

        self._print(f'Handling import:                {import_}\n')

    @typing.override
    def handle_class      (self, class_:handlers.decl.ClassHeaderDeclaration):

        self._print(f'Handling class:                 {class_}\n')

    @typing.override
    def handle_class_end  (self):

        self._print(f'Handling end of class\n')

    @typing.override
    def handle_initializer(self, initializer:handlers.decl.InitializerDeclaration):

        self._print(F'Handling initializer:           {initializer}\n')

    @typing.override
    def handle_constructor(self, constructor:handlers.decl.ConstructorDeclaration):

        self._print(f'Handling constructor:           {constructor}\n')

    @typing.override
    def handle_attribute  (self, attribute:handlers.decl.AttributeDeclaration):

        self._print(f'Handling attribute:             {attribute}\n')

    @typing.override
    def handle_method     (self, method:handlers.decl.MethodDeclaration):

        self._print(f'Handling method:                {method}\n')

    @typing.override
    def handle_enum_value (self, enumvalue:handlers.decl.EnumValueDeclaration):

        self._print(f'Handling enum value:            {enumvalue}\n')

    @typing.override
    def handle_comment    (self, comment:model.Comment):

        self._print(f'Handling comment:               {comment}\n')

class SilentHandler(handlers.entity.Handler):

    @typing.override
    def handle_package    (self, package    :handlers.decl.PackageDeclaration): pass
    @typing.override
    def handle_import     (self, import_    :handlers.decl.ImportDeclaration): pass
    @typing.override
    def handle_class      (self, class_     :handlers.decl.ClassHeaderDeclaration): pass
    @typing.override
    def handle_class_end  (self): pass
    @typing.override
    def handle_initializer(self, initializer:handlers.decl.InitializerDeclaration): pass
    @typing.override
    def handle_constructor(self, constructor:handlers.decl.ConstructorDeclaration): pass
    @typing.override
    def handle_attribute  (self, attribute  :handlers.decl.AttributeDeclaration): pass
    @typing.override
    def handle_method     (self, method     :handlers.decl.MethodDeclaration): pass
    @typing.override
    def handle_enum_value (self, enumvalue  :handlers.decl.EnumValueDeclaration): pass
    @typing.override
    def handle_comment    (self, comment    :model.Comment): pass
