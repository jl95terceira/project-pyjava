_DEBUG = 1

import typing

import javasp_l1_state as state
import javasp_l1_exc   as exc
import javasp_model    as model
import javasp_words    as words
from javasp_l2 import L2Handler

ACCESS_MOD_NAMES_SET        = {x.name   for x in model.AccessModifiers.values()}
ACCESS_MOD_MAP_BY_NAME      = {x.name:x for x in model.AccessModifiers.values()}
FINALITY_TYPE_NAMES_SET     = {x.name   for x in model.FinalityTypes  .values()}
FINALITY_TYPE_MAP_BY_NAME   = {x.name:x for x in model.FinalityTypes  .values()}
CLASS_TYPE_NAMES_SET        = {x.name   for x in model.ClassTypes     .values()}
CLASS_TYPE_MAP_BY_NAME      = {x.name:x for x in model.ClassTypes     .values()}

class L1Handler:

    def __init__                    (self):

        self._next_handler                                = L2Handler()
        self._part             :str                       = ''
        self._line             :str                       = ''
        self._class_name_stack :list[str]                 = list()
        # resettable state
        self._state                                       = state.States    .BEGIN
        self._args_state                                  = state.ArgsStates.BEGIN
        self._handle                                      = self._handle_default
        self._package          :str                 |None = None
        self._static           :bool                      = False
        self._imported         :str                 |None = None
        self._access           :model.AccessModifier|None = None
        self._finality         :model.FinalityType  |None = None
        self._class_type       :model.ClassType     |None = None
        self._class_name       :str                 |None = None
        self._class_extends    :str                 |None = None
        self._class_implements :list[str]                 = list()
        self._type_name        :str                 |None = None
        self._generic_depth    :int                       = 0
        self._attr_name        :str                 |None = None
        self._body_parts       :list[str]                 = list()
        self._arg_name         :str                 |None = None
        self._arg_type_name    :str                 |None = None
        self._args             :dict[str,model.Argument]  = dict()
        self._body_scope_depth:int                        = 1

    def _reset                      (self):

        self._state             = state.States    .BEGIN
        self._args_state        = state.ArgsStates.BEGIN
        self._package           = None
        self._static            = False
        self._imported          = None
        self._access            = None
        self._finality          = None
        self._class_type        = None
        self._class_name        = None
        self._class_extends     = None
        self._class_implements .clear()
        self._type_name         = None
        self._generic_depth     = 0
        self._attr_name         = None
        self._body_parts       .clear()
        self._body_scope_depth  = 1
        self._arg_name          = None
        self._arg_type_name     = None
        self._args             .clear()

    def _state_setter               (self, state_:state.State):

        def _f():

            self._state = state_

        return _f

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.PACKAGE_PRIVATE

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_import               (self):

        self._next_handler.handle_import(name  =self._imported,
                                         static=self._static)
        self._reset()

    def _flush_package              (self):

        self._next_handler.handle_package(name=self._package)
        self._reset()

    def _flush_class                (self):

        self._next_handler.handle_class(name      =self._class_name, 
                                        static    =self._static,
                                        access    =self._coerce_access(self._access),
                                        finality  =self._coerce_finality(self._finality),
                                        type      =self._class_type,
                                        extends   =self._class_extends,
                                        implements=self._class_implements)
        self._class_name_stack.append(self._class_name)
        self._reset()

    def _flush_class_end            (self):

        self._class_name_stack.pop()
        self._next_handler.handle_class_end()
        self._reset()

    def _flush_static_constructor   (self): 
        
        self._next_handler.handle_static_constructor(body=''.join(self._body_parts))
        self._reset()

    def _flush_constructor          (self): 
        
        self._next_handler.handle_constructor(body=''.join(self._body_parts))
        self._reset()

    def _flush_attr_decl            (self):

        self._next_handler.handle_attr(name     =self._attr_name, 
                                       static   =self._static,
                                       final    =self._finality is model.FinalityTypes.FINAL,
                                       access   =self._coerce_access(self._access), 
                                       type_name=self._type_name,
                                       value    =None)
        self._reset()

    def _flush_attr_declinit        (self):

        self._next_handler.handle_attr(name     =self._attr_name, 
                                       static   =self._static,
                                       final    =self._finality is model.FinalityTypes.FINAL,
                                       access   =self._coerce_access(self._access), 
                                       type_name=self._type_name,
                                       value    =''.join(self._body_parts))
        self._reset()

    def _flush_method_decl          (self): 
        
        self._next_handler.handle_method(name      =self._attr_name,
                                         static    =self._static,
                                         access    =self._coerce_access(self._access),
                                         finality  =self._coerce_finality(self._finality),
                                         type_name =self._type_name,
                                         args      =self._args,
                                         body      =None)
        self._reset()

    def _flush_method_impl          (self): 
        
        self._next_handler.handle_method(name      =self._attr_name,
                                         static    =self._static,
                                         access    =self._coerce_access(self._access),
                                         finality  =self._coerce_finality(self._finality),
                                         type_name =self._type_name,
                                         args      =self._args,
                                         body      =''.join(self._body_parts))
        self._reset()

    def _store_implements           (self):

        self._class_implements.append(self._part)
        self._state = state.States.CLASS_IMPLEMENTS_NAMED

    def _store_method_arg_type_name (self):

        if self._part == words.FINAL:

            self._finality = model.FinalityTypes.FINAL
            return

        self._arg_type_name = self._part
        self._state         = state.States.METHOD_ARG_TYPED

    def _store_method_arg           (self):

        self._args[self._arg_name] = model.Argument(type_name=self._arg_type_name, final=self._finality is model.FinalityTypes.FINAL)
        self._arg_name       = None
        self._arg_type_name  = None

    def _parse_body_part            (self, after:typing.Callable[[],None]):

        if self._part == words.BRACE_OPEN:

            self._body_scope_depth += 1

        elif self._part == words.BRACE_CLOSE:

            self._body_scope_depth -= 1
            if self._body_scope_depth == 0:

                after()
                return

        self._body_parts.append(self._part)

    def _parse_signature            (self, after:typing.Callable[[],None]):
    
        if self._part == words.FINAL:

            self._finality = model.FinalityTypes.FINAL

        else:

            self._arg_type_name = self._part
            self._state         = arg_typed_state
    
    def _handle_default             (self):

        if   self._state is state.States.BEGIN:

            if   self._part == words.SEMICOLON  : pass

            elif self._part == words.BRACE_OPEN : 
                
                if self._static and (self._type_name is None): 
                    
                    self._state = state.States.STATIC_CONSTRUCTOR_BODY
                    
                else:

                    self._flush_class()

            elif self._part == words.BRACE_CLOSE: 
                
                self._flush_class_end()

            elif self._part == words.IMPORT     : self._state = state.States.IMPORT

            elif self._part == words.PACKAGE    : self._state = state.States.PACKAGE

            elif self._part in FINALITY_TYPE_NAMES_SET: 
                
                if self._finality is not None: raise exc.Exception(self._line)
                self._finality = FINALITY_TYPE_MAP_BY_NAME[self._part]

            elif self._part in ACCESS_MOD_NAMES_SET:

                if self._access is not None: raise exc.Exception(self._line)
                self._access = ACCESS_MOD_MAP_BY_NAME[self._part]

            elif self._part in CLASS_TYPE_NAMES_SET:

                if self._class_type is not None: raise exc.Exception(self._line)
                self._class_type = CLASS_TYPE_MAP_BY_NAME[self._part]
                self._state = state.States.CLASS_BEGIN

            elif self._part == words.STATIC    :

                if self._static: raise exc.Exception(self._line)
                self._static = True

            elif self._part == words.ATSIGN    : 
                
                self._state = state.States.ANNOTATION

            else: 
                
                self._type_name  = self._part
                self._state      = state.States.TYPED_BEGIN

            return
        
        elif self._state is state.States.PACKAGE:

            if self._package is None: 

                self._package = self._part
            
            elif self._part == words.SEMICOLON:

                self._flush_package()

            else:

                self._package += self._part

            return
        
        elif self._state is state.States.IMPORT:

            if self._imported is None: 

                if self._part == words.STATIC: 
                    
                    self._static = True
                    return
                
                self._imported = self._part

            elif self._part == words.SEMICOLON:

                self._flush_import()
                return

            else:

                self._imported += self._part

            return
        
        elif self._state is state.States.ANNOTATION:

            self._next_handler.handle_annotation(self._part)
            self._reset()
            return
        
        elif self._state is state.States.CLASS_BEGIN:

            self._class_name  = self._part
            self._state = state.States.CLASS_AFTER_NAME
            return

        elif self._state is state.States.CLASS_AFTER_NAME:

            if   self._part == words.EXTENDS:

                if self._class_extends is not None: raise exc.ClassException(self._line)
                self._state = state.States.CLASS_EXTENDS

            elif self._part == words.IMPLEMENTS:

                if self._class_implements: raise exc.ClassException(self._line)
                self._state = state.States.CLASS_IMPLEMENTS

            elif self._part == words.BRACE_OPEN:

                self._flush_class()

            else: raise exc.ClassException(self._line)
            return

        elif self._state is state.States.CLASS_EXTENDS:

            self._class_extends = self._part
            self._state   = state.States.CLASS_AFTER_NAME
            return

        elif self._state is state.States.CLASS_IMPLEMENTS:

            self._store_implements()
            return

        elif self._state is state.States.CLASS_IMPLEMENTS_NAMED:

            if   self._part == words.COMMA:

                self._state = state.States.CLASS_IMPLEMENTS_AFTER

            elif self._part == words.BRACE_OPEN:

                self._flush_class()

            else:raise exc.ClassImplementsException(self._line)
            return
        
        elif self._state is state.States.CLASS_IMPLEMENTS_AFTER:

            self._store_implements()
            return

        elif self._state is state.States.STATIC_CONSTRUCTOR_BODY:

            self._parse_body_part(after=self._flush_static_constructor)
            return

        elif self._state is state.States.TYPED_BEGIN:

            if   self._part in words.ANGLE_OPEN: # generic type - nest

                self._type_name += self._part
                self._generic_depth += 1

            elif self._part in words.ANGLE_CLOSE: # generic type - de-nest

                self._type_name += self._part
                self._generic_depth -= 1

            elif self._generic_depth > 0: # generic type

                self._type_name += self._part

            elif self._part == words.PARENTH_OPEN:
                
                if (self._type_name == self._class_name_stack[-1]): # constructor, since previously we got a word equal to the class' name

                    self._state = state.States.CONSTRUCTOR_SIGNATURE

                else:

                    raise exc.Exception(self._line)

            else:

                self._attr_name  = self._part
                self._state = state.States.TYPED_NAMED

            return
        
        elif self._state is state.States.TYPED_NAMED:

            if  self._part == words.SEMICOLON:

                self._flush_attr_decl()
            
            elif self._part == words.EQUALSIGN:

                self._state = state.States.ATTR_INITIALIZE
            
            elif self._part == words.PARENTH_OPEN:

                self._state = state.States.METHOD_SIGNATURE

            else: raise exc.AttributeException(self._line)
            return
            
        elif self._state is state.States.CONSTRUCTOR_SIGNATURE:

            self._parse_signature(arg_typed_state=state.States.CONSTRUCTOR_ARG_TYPED)
            return
        
        elif self._state is state.States.CONSTRUCTOR_BODY:

            self._parse_body_part(after=self._flush_constructor)

        elif self._state is state.States.ATTR_INITIALIZE:

            if self._part == words.SEMICOLON: 
                
                self._flush_attr_declinit()
                return

            else:

                self._body_parts.append(self._part)
                return

        elif self._state is state.States.METHOD_SIGNATURE:

            if self._part == words.PARENTH_CLOSE:

                self._state = state.States.METHOD_DECLARED
                return

            self._parse_signature(arg_typed_state=state.States.METHOD_ARG_TYPED)
            return
        
        elif self._state is state.States.METHOD_DECLARED:

            if   self._part == words.SEMICOLON:

                self._flush_method_decl()
            
            elif self._part == words.BRACE_OPEN:

                self._state = state.States.METHOD_BODY

            else: raise exc.MethodException(self._line)
        
        elif self._state is state.States.METHOD_BODY:

            self._parse_body_part(after=self._flush_method_impl)
            return

        raise NotImplementedError(self._line)

    def _handle_signature           (self, after:typing.Callable[[],None]): 
        
        if self._args_state is state.ArgsStates.TYPED:

            self._arg_name   = self._part
            self._args_state = state.ArgsStates.NAMED
            return
        
        elif self._args_state is state.ArgsStates.NAMED:

            self._store_method_arg()
            if self._part == words.COMMA:

                self._args_state = state.ArgsStates.AFTER
                return
            
            if self._part == words.PARENTH_CLOSE:

                self._args_state = state.States.METHOD_DECLARED
                return

            raise exc.MethodException(self._line)

        elif self._args_state is state.ArgsStates.AFTER:

            self._store_method_arg_type_name()
            return        

    def handle_part     (self, part   :str, line:str): 
        
        def _pad(x:str,v:int): return (lambda s: f'{s}{(v-len(s))*' '}')(x if isinstance(x, str) else str(x))
        if _DEBUG: print(
            _pad(self._state,                        40), 
            _pad("static" if self._static else "",    8), 
            _pad(self._access,                       35), 
            _pad(self._type_name,                    15), 
            repr(part)
        )
        self._part = part
        self._line = line
        self._handle()

    def handle_comment  (self, comment:str, line:str):

        print(f'Hello, comment: {repr(comment)}')

    def handle_spacing  (self, spacing:str, line:str):

        if self._state is state.States.METHOD_BODY:

            self._body_parts.append(spacing)
