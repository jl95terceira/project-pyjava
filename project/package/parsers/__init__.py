import typing

from .   import part, entity, expr, name, package, import_, body, callargs, generics, signature, type, annotation
from ..  import model, handlers

class StreamPrinter(handlers.entity.Handler):

    @typing.override
    def handle_package    (self, package:model.Package):

        print(f'Handling package:               {package}')

    @typing.override
    def handle_import     (self, import_:model.Import):

        print(f'Handling import:                {import_}')

    @typing.override
    def handle_class      (self, class_:model.Class):

        print(f'Handling class:                 {class_}')

    @typing.override
    def handle_class_end  (self):

        print(f'Handling end of class')

    @typing.override
    def handle_initializer      (self, initializer:model.Initializer):

        print(F'Handling initializer:           {initializer}')

    @typing.override
    def handle_constructor(self, constr:model.Constructor):

        print(f'Handling constructor:           {constr}')

    @typing.override
    def handle_attr       (self, attr:model.Attribute):

        print(f'Handling attribute:             {attr}')

    @typing.override
    def handle_method     (self, method:model.Method):

        print(f'Handling method:                {method}')

    @typing.override
    def handle_enum_value (self, enum:model.EnumValue):

        print(f'Handling enum value:            {enum}')

    @typing.override
    def handle_ainterface(self, ainterface: model.AInterface):

        print(f'Handling annotation interface:  {ainterface}')

    @typing.override
    def handle_comment    (self, comment:model.Comment):

        print(f'Handling comment:               {comment}')

class SilentHandler(handlers.entity.Handler):

    @typing.override
    def handle_package    (self, package:model.Package): pass
    @typing.override
    def handle_import     (self, import_:model.Import): pass
    @typing.override
    def handle_class      (self, class_:model.Class): pass
    @typing.override
    def handle_class_end  (self): pass
    @typing.override
    def handle_initializer(self, initializer:model.Initializer): pass
    @typing.override
    def handle_constructor(self, constructor:model.Constructor): pass
    @typing.override
    def handle_attr       (self, attribute:model.Attribute): pass
    @typing.override
    def handle_method     (self, method:model.Method): pass
    @typing.override
    def handle_enum_value (self, enum:model.EnumValue): pass
    @typing.override
    def handle_ainterface (self, ainterface: model.AInterface): pass
    @typing.override
    def handle_comment    (self, comment:model.Comment): pass
