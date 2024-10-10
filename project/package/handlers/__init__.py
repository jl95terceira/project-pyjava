import abc

from project.package import handlers
import typing

class LineHandler(abc.ABC):

    @abc.abstractmethod
    def handle_line                 (self, line:str): ...
    @abc.abstractmethod
    def handle_eof                  (self): ...

class PartsHandler(LineHandler):

    @abc.abstractmethod
    def handle_part                 (self, part:str): ...
    @abc.abstractmethod
    def handle_comment              (self, text:str): ...
    @abc.abstractmethod
    def handle_spacing              (self, spacing:str): ...
    @abc.abstractmethod
    def handle_newline              (self): ...
    
from .. import model

class StreamHandler(abc.ABC): 

    @abc.abstractmethod
    def handle_package           (self, package:model.Package):  ...
    @abc.abstractmethod
    def handle_import            (self, import_:model.Import):  ...
    @abc.abstractmethod
    def handle_annotation        (self, annot:model.Annotation):   ...
    @abc.abstractmethod
    def handle_class             (self, class_:model.Class):  ...
    @abc.abstractmethod
    def handle_class_end         (self, class_end:model.ClassEnd):  ...
    @abc.abstractmethod
    def handle_static_constructor(self, sconstr:model.StaticConstructor):  ...
    @abc.abstractmethod
    def handle_constructor       (self, constr:model.Constructor):  ...
    @abc.abstractmethod
    def handle_attr              (self, attr:model.Attribute):  ...
    @abc.abstractmethod
    def handle_method            (self, method:model.Method):  ...
    @abc.abstractmethod
    def handle_enum_value        (self, enum:model.EnumValue):  ...
    @abc.abstractmethod
    def handle_comment           (self, comment:model.Comment): ...

from . import body, callargs, generics, signature, type, annotation, part, l2, entity


# For now, all we do is print the events of the parsing process.
# TODO: something more useful :)

class PrintStreamHandler(handlers.StreamHandler):

    @typing.override
    def handle_package           (self, package:model.Package):

        print(f'Handling package:               {package}')

    @typing.override
    def handle_import            (self, import_:model.Import):

        print(f'Handling import:                {import_}')

    @typing.override
    def handle_annotation        (self, annot:model.Annotation):

        print(f'Handling annotation:            {annot}')

    @typing.override
    def handle_class             (self, class_:model.Class):

        print(f'Handling class:                 {class_}')

    @typing.override
    def handle_class_end         (self, class_end:model.ClassEnd=model.ClassEnd()):

        print(f'Handling end of class')

    @typing.override
    def handle_static_constructor(self, sconstr:model.StaticConstructor):

        print(F'Handling static constructor:    {sconstr}')

    @typing.override
    def handle_constructor       (self, constr:model.Constructor):

        print(f'Handling constructor:           {constr}')

    @typing.override
    def handle_attr              (self, attr:model.Attribute):

        print(f'Handling attribute:             {attr}')

    @typing.override
    def handle_method            (self, method:model.Method):

        print(f'Handling method:                {method}')

    @typing.override
    def handle_enum_value        (self, enum:model.EnumValue):

        print(f'Handling enum value:            {enum}')

    @typing.override
    def handle_comment           (self, comment:model.Comment):

        print(f'Handling comment:               {comment}')
