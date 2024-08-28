import dataclasses

import javasp_model as model

class L2Handler: 

    def handle_package      (self, name:str): 
        
        print(f'Handling package: {name}')

    def handle_import       (self, name:str,static:bool): 
        
        print(f'Handling{' static' if static else ''} import: {name}')
        
    def handle_annotation   (self, name:str): 
        
        print(f'Handling annotation: {name}')

    def handle_class        (self, name:str, static:bool, access:model.AccessModifier,extends:str|None, implements:list[str]): 
        
        print(f'Handling{'' if not static else ' static'} class: {name} - {access.name if access is not model.AccessModifiers.PACKAGE_PRIVATE else 'package-private'} access, extends {repr(extends)}, implements {repr(implements)}')

    def handle_scope_begin  (self): 

        print(f'Handling scope begin ({repr('{')})')

    def handle_scope_end    (self): 

        print(f'Handling scope end ({repr('}')})')

    def handle_attr_decl    (self, name:str, static:bool, access:model.AccessModifier, type_name:str):

        print(f'Handling declaration of {repr(name)} as {access.name} {repr(type_name)}')

    def handle_attr_declinit(self, name:str, static:bool, access:model.AccessModifier, type_name:str, value:str):

        print(f'Handling declaration of {repr(name)} as {access.name} {repr(type_name)} and initialize = {value}')

    def handle_nest_begin   (self):

        print(f'Handling nest begin ({repr('(')})')

    def handle_nest_end     (self):

        print(f'Handling nest end ({repr(')')})')

    def handle_method_decl  (self, name:str, static:bool, access:model.AccessModifier, type_name:str, args:list[model.Argument]):

        print(f'Handling declaration of {access.name}{' static' if static else ''} method {repr(name)} with arguments ({','.join(f'{arg.type_name} {repr(arg.name)}' for arg in args)}) -> {type_name}')
