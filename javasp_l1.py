_DEBUG = 1

import re
import typing

import javasp_l1_state as state
import javasp_l1_exc   as exc
import javasp_model    as model
import javasp_words    as words
from javasp_l2 import L2Handler

_ACCESS_MOD_NAMES_SET        = {x.keyword   for x in model.AccessModifiers.values()}
_ACCESS_MOD_MAP_BY_NAME      = {x.keyword:x for x in model.AccessModifiers.values()}
_FINALITY_TYPE_NAMES_SET     = {x.keyword   for x in model.FinalityTypes  .values()}
_FINALITY_TYPE_MAP_BY_NAME   = {x.keyword:x for x in model.FinalityTypes  .values()}
_CLASS_TYPE_NAMES_SET        = {x.keyword   for x in model.ClassTypes     .values()}
_CLASS_TYPE_MAP_BY_NAME      = {x.keyword:x for x in model.ClassTypes     .values()}
_WORD_PATTERN                = re.compile('^\\w+$')
_BODY_STATES                 = {state.States.STATIC_CONSTRUCTOR_BODY,
                               state.States.CONSTRUCTOR_BODY,
                               state.States.METHOD_BODY}

class L1Handler:

    def __DEBUGGED(f):

        def g(self:'L1Handler', *a, **ka):

            def _pad(x:str,v:int): return (lambda s: f'{s}{(v-len(s))*' '}')(x if isinstance(x, str) else str(x))
            if _DEBUG: print(
                _pad(f'{self._state}'     , 30), 
                _pad(f'{len(self._handlers_stack)=}', 20),
                #_pad(f'{self._type_state}', 30),
                #_pad(f'{self._sign_state}', 30),
                #_pad(f'{self._body_state}', 30),
                _pad(f'{self._parargs_state}', 30),
                repr(self._part)
            )
            f(self,*a,**ka)
        
        return g

    def __init__                    (self):

        self._next_handler                                      = L2Handler()
        self._part             :str                             = ''
        self._line             :str                             = ''
        self._class_name_stack :list[str]                       = list()
        self._handlers_stack   :list[typing.Callable[[],None]]  = list()
        # resettable state
        self._state                                           = state.States.BEGIN
        self._type_state       :state.TypeState         |None = None
        self._sign_state       :state.SignState         |None = None
        self._body_state       :state.BodyState         |None = None
        self._handle                                          = self._handle_default
        self._package          :str                     |None = None
        self._static           :bool                          = False
        self._imported         :str                     |None = None
        self._access           :model.AccessModifier    |None = None
        self._finality         :model.FinalityType      |None = None
        self._class_type       :model.ClassType         |None = None
        self._class_name       :str                     |None = None
        self._class_extends    :str                     |None = None
        self._class_implements :list[str]                     = list()
        self._attr_type_name   :str                     |None = None
        self._attr_name        :str                     |None = None
        self._arg_name         :str                     |None = None
        self._arg_type_name    :str                     |None = None
        self._sign             :dict[str,model.Argument]      = dict()
        self._sign_after       :typing.Callable[[],None]|None = None
        self._type_name        :str                     |None = None
        self._type_after       :typing.Callable[[],None]|None = None
        self._generictype_depth:int                     |None = None
        self._body_parts       :list[str]                     = list()
        self._body_scope_depth :int                     |None = None
        self._body_after       :typing.Callable[[],None]|None = None
        self._enumv_name       :str                     |None = None
        self._enumv_arg_values :list[str]               |None = list()
        self._parargs_state    :state.ParArgsState      |None = None
        self._parargs_after    :typing.Callable[[],None]|None = None
        self._parargs_value    :str                     |None = None
        self._parargs_depth    :int                     |None = None

    def _reset                      (self, another_state:state.State|None=None):

        self._state             = state.States.BEGIN if another_state is None else another_state
        self._type_state        = None
        self._sign_state        = None
        self._body_state        = None
        self._handle            = self._handle_default
        self._package           = None
        self._static            = False
        self._imported          = None
        self._access            = None
        self._finality          = None
        self._class_type        = None
        self._class_name        = None
        self._class_extends     = None
        self._class_implements .clear()
        self._attr_type_name    = None
        self._attr_name         = None
        self._arg_name          = None
        self._arg_type_name     = None
        self._sign             .clear()
        self._sign_after        = None
        self._type_name         = None
        self._generictype_depth = None
        self._body_parts       .clear()
        self._body_scope_depth  = None
        self._enumv_name        = None
        self._enumv_arg_values .clear()
        self._parargs_state     = None
        self._parargs_after     = None
        self._parargs_value     = None
        self._parargs_depth     = None

    def _stack_handler              (self, handler:typing.Callable[[], None]):

        if _DEBUG: print('STACK HANDLER')
        self._handlers_stack.append(self._handle)
        self._handle = handler

    def _unstack_handler            (self):

        if _DEBUG: print('UNSTACK HANDLER')
        self._handle = self._handlers_stack.pop()

    def _state_setter               (self, state_:state.State):

        return _StateSetter(self, state_).__call__

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.DEFAULT

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_import               (self):

        self._next_handler.handle_import(name  =self._imported,
                                         static=self._static)
        self._reset()

    def _flush_package              (self):

        self._next_handler.handle_package(name=self._package)
        self._reset()

    def _flush_annotation           (self):

        self._next_handler.handle_annotation(self._part)
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
        self._reset(another_state=None              if self._class_type is not model.ClassTypes.ENUM else \
                                  state.States.ENUM)

    def _flush_class_end            (self):

        self._class_name_stack.pop()
        self._next_handler.handle_class_end()
        self._reset()

    def _flush_static_constructor   (self): 
        
        self._next_handler.handle_static_constructor(body=''.join(self._body_parts))
        self._reset()

    def _flush_constructor          (self): 
        
        self._next_handler.handle_constructor(args=self._sign, body=''.join(self._body_parts))
        self._reset()

    def _flush_attr_decl            (self):

        self._next_handler.handle_attr(name     =self._attr_name, 
                                       static   =self._static,
                                       final    =self._finality is model.FinalityTypes.FINAL,
                                       access   =self._coerce_access(self._access), 
                                       type_name=self._attr_type_name,
                                       value    =None)
        self._reset()

    def _flush_attr_declinit        (self):

        self._next_handler.handle_attr(name     =self._attr_name, 
                                       static   =self._static,
                                       final    =self._finality is model.FinalityTypes.FINAL,
                                       access   =self._coerce_access(self._access), 
                                       type_name=self._attr_type_name,
                                       value    =''.join(self._body_parts))
        self._reset()

    def _flush_method_decl          (self): 
        
        self._next_handler.handle_method(name      =self._attr_name,
                                         static    =self._static,
                                         access    =self._coerce_access(self._access),
                                         finality  =self._coerce_finality(self._finality),
                                         type_name =self._attr_type_name,
                                         args      =self._sign,
                                         body      =None)
        self._reset()

    def _flush_method_impl          (self): 
        
        self._next_handler.handle_method(name      =self._attr_name,
                                         static    =self._static,
                                         access    =self._coerce_access(self._access),
                                         finality  =self._coerce_finality(self._finality),
                                         type_name =self._attr_type_name,
                                         args      =self._sign,
                                         body      =''.join(self._body_parts))
        self._reset()

    def _flush_signature_end        (self):

        self._unstack_handler()
        self._sign_state = None
        self._sign_after()

    def _flush_type_end             (self):

        self._unstack_handler()
        self._type_state = None
        self._type_after()
        self._handle    () # re-handle part (word), since it was used only for look-ahead

    def _flush_body                 (self):

        self._unstack_handler()
        self._body_after()

    def _flush_enumv_empty          (self):

        # no handler to unstack - called from default handler directly
        self._next_handler.handle_enum_value(name=self._enumv_name, arg_values=list())

    def _flush_enumv                (self):

        self._unstack_handler()
        self._next_handler.handle_enum_value(name=self._enumv_name, arg_values=self._enumv_arg_values)
        self._parargs_state = None
        self._parargs_after()

    def _store_implements           (self):

        self._class_implements.append(self._part)
        self._state = state.States.CLASS_IMPLEMENTS_NAMED

    def _store_attr_type            (self):

        self._attr_type_name = self._type_name
        self._state = state.States.ATTR_TYPED

    def _store_signature_arg_type_name(self):

        if self._part == words.FINAL:

            self._finality = model.FinalityTypes.FINAL
            return

        self._arg_type_name = self._part
        self._sign_state    = state.SignStates.ONGOING_TYPED

    def _store_signature_arg        (self):

        self._sign[self._arg_name] = model.Argument(type_name=self._arg_type_name, final=self._finality is model.FinalityTypes.FINAL)
        self._arg_name       = None
        self._arg_type_name  = None

    def _store_arg_type             (self):

        self._arg_type_name = self._type_name
        self._sign_state = state.SignStates.ONGOING_TYPED

    def _store_enumv_arg            (self):

        self._enumv_arg_values.append(self._parargs_value)
        self._parargs_value = ''

    def _parse_body                 (self, after:typing.Callable[[],None]):

        self._stack_handler(self._handle_body)
        self._body_state       = state.BodyStates.BEGIN
        self._body_scope_depth = 0
        self._body_after       = after
        self._handle() # re-handle part ('{'), since it was used only for look-ahead

    def _parse_signature            (self, after:typing.Callable[[],None]):
    
        self._stack_handler(self._handle_signature)
        self._sign_state = state.SignStates.BEGIN
        self._sign_after = after
        self._handle() # # re-handle part ('('), since it was used only for look-ahead
    
    def _parse_type                 (self, after:typing.Callable[[],None]):

        self._stack_handler(self._handle_type)
        self._type_state        = state.TypeStates.BEGIN
        self._type_name         = ''
        self._generictype_depth = 0
        self._type_after        = after
        self._handle() # # re-handle part (word), since it was used only for look-ahead

    def _parse_parargs   (self, after:typing.Callable[[],None]):

        self._stack_handler(self._handle_parargs)
        self._parargs_state = state.ParArgsStates.BEGIN
        self._parargs_depth = 0
        self._parargs_after = after
        self._handle() # re-handle part ('('), since it was used only for look-ahead

    @__DEBUGGED
    def _handle_default             (self):

        if   self._state is state.States.BEGIN:

            if   self._part == words.SEMICOLON  : pass

            elif self._part == words.BRACE_OPEN : 
                
                if self._static and (self._attr_type_name is None): 
                    
                    self._state = state.States.STATIC_CONSTRUCTOR_BODY
                    self._parse_body(after=self._flush_constructor)
                    
                else:

                    self._flush_class()

            elif self._part == words.BRACE_CLOSE: 
                
                self._flush_class_end()

            elif self._part == words.IMPORT     : self._state = state.States.IMPORT

            elif self._part == words.PACKAGE    : self._state = state.States.PACKAGE

            elif self._part in _FINALITY_TYPE_NAMES_SET: 
                
                if self._finality is not None: raise exc.FinalityRepeatedException(self._line)
                self._finality = _FINALITY_TYPE_MAP_BY_NAME[self._part]

            elif self._part in _ACCESS_MOD_NAMES_SET:

                if self._access is not None: raise exc.AccessModifierRepeatedException(self._line)
                self._access = _ACCESS_MOD_MAP_BY_NAME[self._part]

            elif self._part in _CLASS_TYPE_NAMES_SET:

                if self._class_type is not None: raise exc.ClassTypeRepeatedException(self._line)
                self._class_type = _CLASS_TYPE_MAP_BY_NAME[self._part]
                self._state = state.States.CLASS_BEGIN

            elif self._part == words.STATIC    :

                if self._static: raise exc.StaticRepeatedException(self._line)
                self._static = True

            elif self._part == words.ATSIGN    : 
                
                self._state = state.States.ANNOTATION

            else: 
                
                self._state = state.States.ATTR_BEGIN
                self._parse_type(after=self._store_attr_type)

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

            self._flush_annotation()
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

        elif self._state is state.States.ATTR_TYPED:

            if self._part == words.PARENTH_OPEN:
                
                if (self._attr_type_name == self._class_name_stack[-1]): # constructor, since previously we got a word equal to the class' name

                    self._state = state.States    .CONSTRUCTOR_SIGNATURE
                    self._parse_signature(after=self._state_setter(state.States.CONSTRUCTOR_DECLARED))

                else:

                    raise exc.MethodOrConstructorException(self._line)

            else:

                self._attr_name  = self._part
                self._state = state.States.ATTR_NAMED

            return
        
        elif self._state is state.States.ATTR_NAMED:

            if   self._part == words.SEMICOLON:

                self._flush_attr_decl()
            
            elif self._part == words.EQUALSIGN:

                self._state = state.States.ATTR_INITIALIZE
            
            elif self._part == words.PARENTH_OPEN:

                self._state = state.States.METHOD_SIGNATURE
                self._parse_signature(after=self._state_setter(state.States.METHOD_DECLARED))

            else: raise exc.AttributeException(self._line)
            return
            
        elif self._state is state.States.CONSTRUCTOR_DECLARED:

            self._state = state.States.CONSTRUCTOR_BODY
            self._parse_body(after=self._flush_constructor)
            return

        elif self._state is state.States.ATTR_INITIALIZE:

            if self._part == words.SEMICOLON: 
                
                self._flush_attr_declinit()
                return

            else:

                self._body_parts.append(self._part)
                return

        elif self._state is state.States.METHOD_DECLARED:

            if   self._part == words.SEMICOLON:

                self._flush_method_decl()
            
            else:

                self._state = state.States.METHOD_BODY
                self._handle_default()

            return
        
        elif self._state is state.States.METHOD_BODY:

            self._parse_body(after=self._flush_method_impl)
            return
        
        elif self._state is state.States.ENUM:

            if   self._part == words.SEMICOLON:

                self._reset()

            elif not _WORD_PATTERN.match(self._part):

                raise exc.EnumValueNameException(self._line)
            
            else:

                self._enumv_name = self._part
                self._state = state.States.ENUM_NAMED

            return

        elif self._state is state.States.ENUM_NAMED:

            if   self._part == words.SEMICOLON:

                self._flush_enumv_empty()
                self._reset()

            elif self._part == words.COMMA:

                self._flush_enumv_empty()
                self._reset(another_state=state.States.ENUM)

            else:
                
                self._parse_parargs(after=self._flush_enumv)

            return

        raise NotImplementedError(self._line)
        
    @__DEBUGGED
    def _handle_signature           (self): 
        
        if   self._sign_state is state.SignStates.BEGIN:

            if  self._part != words.PARENTH_OPEN:

                raise exc.MethodException(self._line)
            
            self._sign_state = state.SignStates.ONGOING

        elif self._sign_state is state.SignStates.ONGOING:

            if   self._part == words.PARENTH_CLOSE:

                self._flush_signature_end()

            elif self._part == words.FINAL:

                self._finality = model.FinalityTypes.FINAL

            else:

                self._parse_type(after=self._store_arg_type)

        elif self._sign_state is state.SignStates.ONGOING_TYPED:

            self._arg_name   = self._part
            self._sign_state = state.SignStates.ONGOING_NAMED
        
        elif self._sign_state is state.SignStates.ONGOING_NAMED:

            self._store_signature_arg()
            if   self._part == words.COMMA:

                self._sign_state = state.SignStates.ONGOING_SEPARATE
            
            elif self._part == words.PARENTH_CLOSE:

                self._flush_signature_end()

            else: raise exc.MethodException(self._line)

        elif self._sign_state is state.SignStates.ONGOING_SEPARATE:

            self._store_signature_arg_type_name()

        else: raise AssertionError(f'{self._sign_state=}')

    @__DEBUGGED
    def _handle_type                (self):

        if self._type_state is state.TypeStates.BEGIN:

            if not _WORD_PATTERN.match(self._part):

                raise exc.TypeException(self._line)
            
            self._type_name  += self._part
            self._type_state  = state.TypeStates.ONGOING

        elif self._type_state is state.TypeStates.ONGOING:

            if   self._part in words.ANGLE_OPEN: # generic type - nest

                self._type_name += self._part
                self._generictype_depth += 1

            elif self._part in words.ANGLE_CLOSE: # generic type - de-nest

                self._type_name += self._part
                self._generictype_depth -= 1

            elif self._generictype_depth > 0: # generic type

                self._type_name += self._part

            elif self._part in {words.SQUARE_OPEN, 
                                words.SQUARE_CLOSED}:
                
                self._type_name += self._part

            elif self._part == words.DOT:

                self._type_name  += self._part
                self._type_state  = state.TypeStates.ONGOING_DOT

            else:

                self._flush_type_end()

        elif self._type_state is state.TypeStates.ONGOING_DOT:

            if not _WORD_PATTERN.match(self._part): raise exc.TypeException(self._line)
            self._type_name  += self._part
            self._type_state  = state.TypeStates.ONGOING

        else: raise AssertionError(f'{self._type_state=}')

    @__DEBUGGED
    def _handle_body                (self):

        if self._body_state is state.BodyStates.BEGIN:

            if self._body_scope_depth != 0:

                raise AssertionError(f'{self._body_scope_depth=}')

            if self._part != words.BRACE_OPEN:

                raise exc.BodyException(self._line)
           
            else:
               
                self._body_state = state.BodyStates.ONGOING
                self._body_scope_depth += 1

        elif self._body_state is state.BodyStates.ONGOING:

            if self._part == words.BRACE_OPEN:

                self._body_scope_depth += 1
                self._body_parts.append(self._part)

            elif self._part == words.BRACE_CLOSE:

                self._body_scope_depth -= 1
                if self._body_scope_depth == 0:

                    self._flush_body()
                
                else:
                    
                    self._body_parts.append(self._part)

        else: raise AssertionError(f'{self._body_state=}')

    @__DEBUGGED
    def _handle_parargs  (self):

        if self._parargs_state is state.ParArgsStates.BEGIN:

            if self._part != words.PARENTH_OPEN:

                raise exc.EnumValueException(self._line)
            
            else:

                self._parargs_state  = state.ParArgsStates.ONGOING
                self._parargs_value  = ''
                self._parargs_depth += 1

        elif self._parargs_state is state.ParArgsStates.ONGOING:

            if self._part == words.PARENTH_CLOSE:

                self._parargs_depth -= 1
                if self._parargs_depth != 0:

                    self._parargs_value += self._part

                else:

                    self._store_enumv_arg()
                    self._flush_enumv    ()

            elif self._part == words.PARENTH_OPEN:

                self._parargs_depth += 1
                self._parargs_value += self._part

            elif self._part == words.COMMA:

                if self._parargs_depth == 0:

                    self._store_enumv_arg()
                    self._parargs_state = state.ParArgsStates.ONGOING_SEP
                
                else:

                    self._parargs_value += self._part

            else:

                self._parargs_value += self._part

        elif self._parargs_state is state.ParArgsStates.ONGOING_SEP: 
            
            if self._part == words.PARENTH_CLOSE: 
                
                raise exc.EnumValueException(self._line)
            
            self._parargs_state = state.ParArgsStates.ONGOING
            self._handle() # re-handle part, since it was used only for look-ahead

        else: raise AssertionError(f'{self._parargs_state=}')

    def handle_part                 (self, part   :str, line:str): 
        
        self._part = part
        self._line = line
        self._handle()

    def handle_comment              (self, comment:str, line:str):

        print(f'Hello, comment: {repr(comment)}')

    def handle_spacing              (self, spacing:str, line:str):

        if   self._state is state.States.ATTR_INITIALIZE:
        
            self._body_parts.append(spacing)

        elif self._state in _BODY_STATES:

            self._body_parts.append(spacing)

    def handle_newline              (self, line:str):

        self.handle_spacing(spacing='\n', line=line)

class _StateSetter:

    def __init__(self, l1:L1Handler, s:state.State):

        self._l1 = l1
        self._s  = s

    def __call__(self): self._l1._state = self._s
