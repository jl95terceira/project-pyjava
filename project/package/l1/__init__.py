_DEBUG          = 0
_DEBUG_HANDLERS = 0

import re
import typing

from .    import state
from .    import exc
from ..   import handlers
from ..   import model
from ..   import words
from ..l2 import L2Handler

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
                _pad(f'{self._state}'     , 35), 
                #_pad(f'{len(self._handlers_stack)=}', 20),
                _pad(f'{self._class_name_stack[-1] if self._class_name_stack else ''}', 10),
                _pad(f'{self._type_state}', 30),
                _pad(f'{self._sign_state}', 30),
                #_pad(f'{self._body_state}', 30),
                _pad(f'{self._parargs_state}', 30),
                repr(self._part)
            )
            f(self,*a,**ka)
        
        return g

    def __init__                    (self, stream_handler:handlers.StreamHandler):

        self._next_handler                                    = stream_handler
        self._part             :str                           = ''
        self._line             :str                           = ''
        self._class_name_stack :list[str]                     = list()
        self._handlers_stack   :list[_Handler]                = list()
        self._handler                                         = _Handler(self._handle_default, name='default')
        # resettable state
        self._state                                           = state.States.DEFAULT
        self._type_state       :state.TypeState         |None = None
        self._sign_state       :state.SignatureState    |None = None
        self._body_state       :state.BodyState         |None = None
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
        self._type_depth:int                            |None = None
        self._body_parts       :list[str]                     = list()
        self._body_depth :int                           |None = None
        self._body_after       :typing.Callable[[],None]|None = None
        self._enumv_name       :str                     |None = None
        self._parargs          :list[str]               |None = list()
        self._parargs_state    :state.ParArgsState      |None = None
        self._parargs_after    :typing.Callable[[],None]|None = None
        self._pararg_value    :str                      |None = None
        self._pararg_depth    :int                      |None = None

    def _reset                      (self, another_state:state.State|None=None):

        self._state             = state.States.DEFAULT if another_state is None else another_state
        self._type_state        = None
        self._sign_state        = None
        self._body_state        = None
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
        self._type_depth        = None
        self._body_parts       .clear()
        self._enumv_name        = None

    def _stack_handler              (self, handler:'_Handler'):

        if _DEBUG_HANDLERS: print(f'STACK HANDLER: {self._handler.name} -> {handler.name}')
        self._handlers_stack.append(self._handler)
        self._handler = handler

    def _unstack_handler            (self):

        if _DEBUG_HANDLERS: print(f'UNSTACK HANDLER: {self._handlers_stack[-1].name} <- {self._handler.name}')
        self._handler = self._handlers_stack.pop()

    def _state_setter               (self, state_:state.State):

        return _StateSetter(self, state_).__call__

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.DEFAULT

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_import               (self):

        self._next_handler.handle_import(model.Import(name  =self._imported,
                                                      static=self._static))
        self._reset()

    def _flush_package              (self):

        self._next_handler.handle_package(model.Package(name=self._package))
        self._reset()

    def _flush_annotation           (self):

        self._next_handler.handle_annotation(self._part)
        self._reset()

    def _flush_class                (self):

        self._next_handler.handle_class(model.Class(name      =self._class_name, 
                                                    static    =self._static,
                                                    access    =self._coerce_access(self._access),
                                                    finality  =self._coerce_finality(self._finality),
                                                    type      =self._class_type,
                                                    extends   =self._class_extends,
                                                    implements=self._class_implements))
        self._class_name_stack.append(self._class_name)
        self._reset(another_state=None              if self._class_type is not model.ClassTypes.ENUM else \
                                  state.States.ENUM)

    def _flush_class_end            (self):

        self._class_name_stack.pop()
        self._next_handler.handle_class_end(model.ClassEnd())
        self._reset()

    def _flush_static_constructor   (self): 
        
        self._next_handler.handle_static_constructor(model.StaticConstructor(body=''.join(self._body_parts)))
        self._reset()

    def _flush_constructor          (self): 
        
        self._next_handler.handle_constructor(model.Constructor(args=self._sign, 
                                                                body=''.join(self._body_parts)))
        self._reset()

    def _flush_attr_decl            (self):

        self._flush_attr(decl_only=True)

    def _flush_attr                 (self, decl_only=False):

        self._next_handler.handle_attr(model.Attribute(name     =self._attr_name, 
                                                       static   =self._static,
                                                       final    =self._finality is model.FinalityTypes.FINAL,
                                                       access   =self._coerce_access(self._access), 
                                                       type_name=self._attr_type_name,
                                                       value    =None if decl_only else ''.join(self._body_parts)))
        self._reset()

    def _flush_method_decl          (self): 
        
        self._flush_method(decl_only=True)

    def _flush_method               (self, decl_only=False): 
        
        self._next_handler.handle_method(model.Method(name      =self._attr_name,
                                                      static    =self._static,
                                                      access    =self._coerce_access(self._access),
                                                      finality  =self._coerce_finality(self._finality),
                                                      type_name =self._attr_type_name,
                                                      args      =self._sign,
                                                      body      =None if decl_only else ''.join(self._body_parts)))
        self._reset()

    def _flush_signature            (self):

        self._unstack_handler()
        self._sign_state = None
        self._sign_after()
        self._sign_after = None
        #self._sign      .clear()

    def _flush_type                 (self):

        self._unstack_handler()
        self._type_state = None
        self._type_after()
        self._handler    () # re-handle part (word), since it was used only for look-ahead

    def _flush_body                 (self):

        self._unstack_handler()
        self._body_parts.clear()
        self._body_depth = None
        self._body_after()
        self._body_after = None

    def _flush_enumv_empty          (self):

        self._flush_enumv(no_args=True)

    def _flush_enumv                (self, no_args=False):

        self._next_handler.handle_enum_value(model.EnumValue(name      =self._enumv_name, 
                                                             arg_values=list() if no_args else self._parargs))
        self._state = state.States.ENUM_DEFINED

    def _flush_parargs              (self):

        if self._pararg_value:

            self._store_pararg()

        self._unstack_handler()
        self._parargs_state  = None
        self._pararg_value   = None
        self._pararg_depth   = None
        self._parargs_after()
        self._parargs       .clear()
        self._parargs_after = None

    def _store_attr_type            (self):

        self._attr_type_name = self._type_name
        self._state = state.States.ATTR_TYPED

    def _store_sign_arg             (self):

        self._sign[self._arg_name] = model.Argument(type_name=self._arg_type_name, final=self._finality is model.FinalityTypes.FINAL)
        self._arg_name       = None
        self._arg_type_name  = None

    def _store_arg_type             (self):

        self._arg_type_name = self._type_name
        self._sign_state = state.SignatureStates.ARG_TYPED

    def _store_pararg               (self):

        self._parargs.append(self._pararg_value)
        self._pararg_value = ''
        self._pararg_depth = 0

    def _parse_body                 (self, after:typing.Callable[[],None]):

        self._stack_handler(_Handler(self._handle_body, name='BODY'))
        self._body_state       = state.BodyStates.BEGIN
        self._body_depth       = 0
        self._body_after       = after
        self._handler() # re-handle part ('{'), since it was used only for look-ahead

    def _parse_signature            (self, after:typing.Callable[[],None]):
    
        self._stack_handler(_Handler(self._handle_signature, name='SIGNATURE'))
        self._sign_state = state.SignatureStates.BEGIN
        self._sign_after = after
        self._handler() # re-handle part ('('), since it was used only for look-ahead
    
    def _parse_type                 (self, after:typing.Callable[[],None]):

        self._stack_handler(_Handler(self._handle_type, name='TYPE'))
        self._type_state        = state.TypeStates.BEGIN
        self._type_name         = ''
        self._type_depth        = 0
        self._type_after        = after
        self._handler() # re-handle part (word), since it was used only for look-ahead

    def _parse_parargs   (self, after:typing.Callable[[],None]):

        self._stack_handler(_Handler(self._handle_parargs, name='PARARGS'))
        self._parargs_state = state.ParArgsStates.BEGIN
        self._pararg_value  = ''
        self._pararg_depth  = 0
        self._parargs_after = after
        self._handler() # re-handle part ('('), since it was used only for look-ahead

    @__DEBUGGED
    def _handle_default             (self):

        if   self._state is state.States.DEFAULT:

            if   self._part == words.SEMICOLON  : pass

            elif self._part == words.BRACE_OPEN : 
                
                if self._static and (self._attr_type_name is None): 
                    
                    self._state = state.States.STATIC_CONSTRUCTOR_BODY
                    self._parse_body(after=self._flush_static_constructor)
                    
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
                self._state      = state.States.CLASS_BEGIN

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

            self._class_implements.append(self._part)
            self._state = state.States.CLASS_IMPLEMENTS_NAMED
            return

        elif self._state is state.States.CLASS_IMPLEMENTS_NAMED:

            if   self._part == words.COMMA:

                self._state = state.States.CLASS_IMPLEMENTS_AFTER

            elif self._part == words.BRACE_OPEN:

                self._flush_class()

            else:raise exc.ClassImplementsException(self._line)
            return
        
        elif self._state is state.States.CLASS_IMPLEMENTS_AFTER:

            self._state = state.States.CLASS_IMPLEMENTS
            self._handler()
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
                
                self._flush_attr()
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

            self._parse_body(after=self._flush_method)
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

            if   self._part in {words.SEMICOLON,
                                words.COMMA}:

                self._flush_enumv_empty()
                self._handler() # re-handle part (either semicolon or comma), as it was used only for look-ahead

            else:
                
                self._parse_parargs(after=self._flush_enumv)

            return

        elif self._state is state.States.ENUM_DEFINED:

            if self._part == words.SEMICOLON:

                self._reset()

            elif self._part is words.COMMA:

                self._reset(another_state=state.States.ENUM)

            else: raise exc.EnumValueException(self._line)
            return

        raise NotImplementedError(self._line)
        
    @__DEBUGGED
    def _handle_signature           (self): 
        
        if   self._sign_state is state.SignatureStates.BEGIN:

            if  self._part != words.PARENTH_OPEN:

                raise exc.MethodOpenException(self._line)
            
            self._sign_state = state.SignatureStates.DEFAULT

        elif self._sign_state is state.SignatureStates.DEFAULT:

            if   self._part == words.PARENTH_CLOSE:

                self._flush_signature()

            elif self._part == words.FINAL:

                self._finality = model.FinalityTypes.FINAL

            else:

                self._parse_type(after=self._store_arg_type)

        elif self._sign_state is state.SignatureStates.ARG_TYPED:

            self._arg_name   = self._part
            self._sign_state = state.SignatureStates.ARG_NAMED
        
        elif self._sign_state is state.SignatureStates.ARG_NAMED:

            if   self._part == words.COMMA:

                self._store_sign_arg()
                self._sign_state = state.SignatureStates.ARG_SEPARATE
            
            elif self._part == words.PARENTH_CLOSE:

                self._store_sign_arg()
                self._flush_signature    ()

            else: raise exc.MethodAfterNameException(self._line)

        elif self._sign_state is state.SignatureStates.ARG_SEPARATE:

            if not _WORD_PATTERN.match(self._part): raise exc.MethodException(self._line)
            self._sign_state = state.SignatureStates.DEFAULT
            self._handler()

        else: raise AssertionError(f'{self._sign_state=}')

    @__DEBUGGED
    def _handle_type                (self):

        if self._type_state   is state.TypeStates.BEGIN:

            if not _WORD_PATTERN.match(self._part):

                raise exc.TypeException(self._line)
            
            self._type_name  += self._part
            self._type_state  = state.TypeStates.DEFAULT

        elif self._type_state is state.TypeStates.DEFAULT:

            if   self._part in words.ANGLE_OPEN: # generic type - nest

                self._type_name += self._part
                self._type_depth += 1

            elif self._part in words.ANGLE_CLOSE: # generic type - de-nest

                self._type_name += self._part
                self._type_depth -= 1

            elif self._type_depth > 0: # generic type

                self._type_name += self._part

            elif self._part in {words.SQUARE_OPEN, 
                                words.SQUARE_CLOSED}:
                
                self._type_name += self._part

            elif self._part == words.DOT:

                self._type_name  += self._part
                self._type_state  = state.TypeStates.AFTERDOT

            else:

                self._flush_type()

        elif self._type_state is state.TypeStates.AFTERDOT:

            if not _WORD_PATTERN.match(self._part): raise exc.TypeException(self._line)
            self._type_name  += self._part
            self._type_state  = state.TypeStates.DEFAULT

        else: raise AssertionError(f'{self._type_state=}')

    @__DEBUGGED
    def _handle_body                (self):

        if self._body_state is state.BodyStates.BEGIN:

            if self._body_depth != 0:

                raise AssertionError(f'{self._body_depth=}')

            if self._part != words.BRACE_OPEN:

                raise exc.BodyException(self._line)
           
            else:
               
                self._body_state = state.BodyStates.ONGOING
                self._body_depth += 1

        elif self._body_state is state.BodyStates.ONGOING:

            if self._part == words.BRACE_OPEN:

                self._body_depth += 1
                self._body_parts.append(self._part)

            elif self._part == words.BRACE_CLOSE:

                self._body_depth -= 1
                if self._body_depth == 0:

                    self._flush_body()
                
                else:
                    
                    self._body_parts.append(self._part)

        else: raise AssertionError(f'{self._body_state=}')

    @__DEBUGGED
    def _handle_parargs             (self):

        if self._parargs_state is state.ParArgsStates.BEGIN:

            if self._part != words.PARENTH_OPEN:

                raise exc.EnumValueException(self._line)
            
            else:

                self._parargs_state  = state.ParArgsStates.DEFAULT
                self._pararg_value  = ''
                self._pararg_depth += 1

        elif self._parargs_state is state.ParArgsStates.DEFAULT:

            if self._part == words.PARENTH_CLOSE:

                self._pararg_depth -= 1
                if self._pararg_depth != 0:

                    self._pararg_value += self._part

                else:

                    self._flush_parargs()

            elif self._part == words.PARENTH_OPEN:

                self._pararg_depth += 1
                self._pararg_value += self._part

            elif self._part == words.COMMA:

                if self._pararg_depth == 0:

                    self._store_pararg()
                    self._parargs_state = state.ParArgsStates.SEPARATE
                
                else:

                    self._pararg_value += self._part

            else:

                self._pararg_value += self._part

        elif self._parargs_state is state.ParArgsStates.SEPARATE: 
            
            if self._part == words.PARENTH_CLOSE: 
                
                raise exc.EnumValueException(self._line)
            
            self._parargs_state = state.ParArgsStates.DEFAULT
            self._handler() # re-handle part, since it was used only for look-ahead

        else: raise AssertionError(f'{self._parargs_state=}')

    def handle_part                 (self, part   :str, line:str): 
        
        self._part = part
        self._line = line
        self._handler()

    def handle_comment              (self, text   :str, line:str):

        self._next_handler.handle_comment(comment=model.Comment(text=text))

    def handle_spacing              (self, spacing:str, line:str):

        if   self._state is state.States.ATTR_INITIALIZE:
        
            self._body_parts.append(spacing)

        elif self._state in _BODY_STATES:

            self._body_parts.append(spacing)

    def handle_newline              (self, line   :str):

        self.handle_spacing(spacing='\n', line=line)

class _StateSetter:

    def __init__(self, l1:L1Handler, s:state.State):

        self._l1 = l1
        self._s  = s

    def __call__(self): self._l1._state = self._s

class _Handler:

    def __init__(self, callable:typing.Callable[[],None], name:str): 
        
        self._callable = callable
        self.name      = name

    def __call__(self): self._callable()
