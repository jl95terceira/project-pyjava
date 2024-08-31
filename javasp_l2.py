import dataclasses

import javasp_model as model

def _access_name(access:model.AccessModifier):

    return access.name if access is not model.AccessModifiers.PACKAGE_PRIVATE else 'package-private'

# For now, all we do is print the events of the parsing process.
# TODO: something more useful :)

class L2Handler: 

    def handle_package           (self, name:str): 
        
        print(f'Handling package: {name}')

    def handle_import            (self, name:str,static:bool): 
        
        print(f'Handling{' static' if static else ''} import: {name}')
        
    def handle_annotation        (self, name:str): 
        
        print(f'Handling annotation: {name}')

    def handle_class             (self, name:str, static:bool, access:model.AccessModifier, finality:model.FinalityType, type:model.ClassType, extends:str|None, implements:list[str]): 
        
        print(f'Handling {'' if finality is model.FinalityTypes.DEFAULT else finality.name}{'' if not static else ' static'} {type.name}: {name} - {access.name if access is not model.AccessModifiers.PACKAGE_PRIVATE else 'package-private'} access, extends {repr(extends)}, implements {repr(implements)}')

    def handle_class_end         (self): 

        print(f'Handling end of class')

    def handle_static_constructor(self, body:str):

        print(F'Handling static constructor\n  Body: {repr(body)}')

    def handle_constructor       (self, args:dict[str,model.Argument], body:str):

        print(f'Handling constructor with args {repr(args)}')

    def handle_attr              (self, name:str, static:bool, access:model.AccessModifier, final:bool, type_name:str, value:str|None):

        print(f'Handling declaration of {repr(name)} as {_access_name(access)}{' final' if final else ''} {repr(type_name)}{f' and initialize = {value}' if value is not None else ''}')

    def handle_method            (self, name:str, static:bool, access:model.AccessModifier, finality:model.FinalityType, type_name:str, args:dict[str,model.Argument], body:str|None):

        print(f'Handling declaration of {_access_name(access)}{' static' if static else ''}{'' if finality is model.FinalityTypes.DEFAULT else f' {finality.name}'} method {repr(name)} with arguments ({','.join(f'{'' if not v.final else 'final '}{v.type_name} {repr(a)}' for a,v in args.items())}) -> {type_name}\n  {f'Body: {repr(body)}' if body is not None else 'No body'}')
