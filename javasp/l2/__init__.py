from .. import model

def _join_args(*aa:str):

    return f'\n{'\n  '.join(('', *aa))}\n'

# For now, all we do is print the events of the parsing process.
# TODO: something more useful :)

class L2Handler: 

    def handle_package           (self, name:str): 
        
        print(f'Handling package: {name}')

    def handle_import            (self, name:str,static:bool): 
        
        print(f'Handling import: {name}{_join_args(f'{static    =}')}')
        
    def handle_annotation        (self, name:str): 
        
        print(f'Handling annotation: {name}')

    def handle_class             (self, name:str, static:bool, access:model.AccessModifier, finality:model.FinalityType, type:model.ClassType, extends:str|None, implements:list[str]): 
        
        print(f'Handling class: {name}{_join_args(f'{access    =}',
                                                  f'{static    =}',
                                                  f'{finality  =}',
                                                  f'{type      =}',
                                                  f'{extends   =}',
                                                  f'{implements=}')}')

    def handle_class_end         (self): 

        print(f'Handling end of class')

    def handle_static_constructor(self, body:str):

        print(F'Handling static constructor{_join_args(f'{body      =}')}')

    def handle_constructor       (self, args:dict[str,model.Argument], body:str):

        print(f'Handling constructor:{_join_args(f'{args      =}',
                                                 f'{body      =}')}')

    def handle_attr              (self, name:str, static:bool, access:model.AccessModifier, final:bool, type_name:str, value:str|None):

        print(f'Handling attribute: {name}{_join_args(f'{access    =}',
                                                      f'{static    =}',
                                                      f'{final     =}',
                                                      f'{type_name =}',
                                                      f'{value     =}')}')

    def handle_method            (self, name:str, static:bool, access:model.AccessModifier, finality:model.FinalityType, type_name:str, args:dict[str,model.Argument], body:str|None):

        print(f'Handling method: {name}{_join_args(f'{access    =}',
                                                   f'{static    =}',
                                                   f'{finality  =}',
                                                   f'{type_name =}',
                                                   f'{args      =}',
                                                   f'{body      =}')}')

    def handle_enum_value        (self, name:str, arg_values:list[str]):

        print(f'Handling enum value: {name}{_join_args(f'{arg_values=}')}')
