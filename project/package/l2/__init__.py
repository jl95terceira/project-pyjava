import typing

from .. import handlers
from .. import model

# For now, all we do is print the events of the parsing process.
# TODO: something more useful :)

class L2Handler(handlers.StreamHandler): 

    @typing.override
    def handle_package           (self, package:model.Package): 
        
        print(f'Handling package: {package}\n')

    @typing.override
    def handle_import            (self, import_:model.Import): 
        
        print(f'Handling import: {import_}\n')
        
    @typing.override
    def handle_annotation        (self, annot:model.Annotation): 
        
        print(f'Handling annotation: {annot}\n')

    @typing.override
    def handle_class             (self, class_:model.Class): 
        
        print(f'Handling class: {class_}\n')

    @typing.override
    def handle_class_end         (self, class_end:model.ClassEnd=model.ClassEnd()): 

        print(f'Handling end of class\n')

    @typing.override
    def handle_static_constructor(self, sconstr:model.StaticConstructor):

        print(F'Handling static constructor: {sconstr}\n')

    @typing.override
    def handle_constructor       (self, constr:model.Constructor):

        print(f'Handling constructor:{constr}\n')

    @typing.override
    def handle_attr              (self, attr:model.Attribute):

        print(f'Handling attribute: {attr}\n')
            
    @typing.override
    def handle_method            (self, method:model.Method):

        print(f'Handling method: {method}\n')

    @typing.override
    def handle_enum_value        (self, enum:model.EnumValue):

        print(f'Handling enum value: {enum}\n')

    @typing.override
    def handle_comment           (self, comment:model.Comment):

        print(f'Handling comment: {comment}\n')