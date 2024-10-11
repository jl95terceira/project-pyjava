_DEBUG_HANDLERS = 0

import abc
from   collections import defaultdict
import re
import typing

from .            import exc, state
from ...          import handlers, model, util, words, parsers
from ...batteries import *

_INHERIT_TYPE_MAP_BY_KEYWORD = {words.EXTENDS   :model.InheritanceTypes.EXTENDS,
                                words.IMPLEMENTS:model.InheritanceTypes.IMPLEMENTS}

_INHERIT_TYPE_KEYWORDS       = set(_INHERIT_TYPE_MAP_BY_KEYWORD)
_ACCESS_MOD_MAP_BY_KEYWORD   = {words.PUBLIC    :model.AccessModifiers.PUBLIC,
                                ''              :model.AccessModifiers.DEFAULT,
                                words.PROTECTED :model.AccessModifiers.PROTECTED,
                                words.PRIVATE   :model.AccessModifiers.PRIVATE}
_ACCESS_MOD_KEYWORDS         = set(_ACCESS_MOD_MAP_BY_KEYWORD)
_FINALITY_TYPE_MAP_BY_KEYWORD= {''              :model.FinalityTypes.DEFAULT,
                                words.ABSTRACT  :model.FinalityTypes.ABSTRACT,
                                words.FINAL     :model.FinalityTypes.FINAL}
_FINALITY_TYPE_KEYWORDS      = set(_FINALITY_TYPE_MAP_BY_KEYWORD)
_CLASS_TYPE_MAP_BY_KEYWORD   = {words.CLASS     :model.ClassTypes.CLASS,
                                words.INTERFACE :model.ClassTypes.INTERFACE,
                                words.ENUM      :model.ClassTypes.ENUM}
_CLASS_TYPE_KEYWORDS         = set(_CLASS_TYPE_MAP_BY_KEYWORD)
_WORD_PATTERN                = re.compile('^\\w+$')

class StackingSemiParser(handlers.part.Handler, abc.ABC):

    def __init__(self):

        self._subhandler:handlers.part.Handler|None = None

    def _stack_handler              (self, handler:handlers.part.Handler):

        if _DEBUG_HANDLERS: print(f'STACK HANDLER: {handler.__class__.__module__}::{handler.__class__.__name__}')
        self._subhandler = handler
        self._subhandler.handle_line(self._line)

    def _unstack_handler            (self):

        if _DEBUG_HANDLERS: print(f'UNSTACK HANDLER: {self._subhandler.__class__.__module__}::{self._subhandler.__class__.__name__}')
        self._subhandler = None

    def _unstacking                 (self, f): return ChainedCall(lambda *a, **ka: self._unstack_handler(), f)

    @typing.override
    def handle_line                 (self, line:str):

        self._line = line
        if self._subhandler is not None: self._subhandler.handle_line(line)
        else                           : self.   _default_handle_line(line)

    @typing.override
    def handle_part                 (self, part:str): 
        
        if self._subhandler is not None: self._subhandler.handle_part(part)
        else                           : self.   _default_handle_part(part)

    @typing.override
    def handle_comment              (self, text:str):

        if self._subhandler is not None: self._subhandler.handle_comment(text)
        else                           : self.   _default_handle_comment(text)

    @typing.override
    def handle_spacing              (self, spacing:str):

        if self._subhandler is not None: self._subhandler.handle_spacing(spacing)
        else                           : self.   _default_handle_spacing(spacing)

    @typing.override
    def handle_newline              (self):

        if self._subhandler is not None: self._subhandler.handle_newline()
        else                           : self.   _default_handle_newline()

    @typing.override
    def handle_eof                  (self):
        
        if self._subhandler is not None: self._subhandler.handle_eof()
        else                           : self.   _default_handle_eof()

    @abc.abstractmethod
    def _default_handle_line        (self, line:str): ...

    @abc.abstractmethod
    def _default_handle_part        (self, part:str): ...

    @abc.abstractmethod
    def _default_handle_comment     (self, text:str): ...

    @abc.abstractmethod
    def _default_handle_spacing     (self, spacing:str): ...

    @abc.abstractmethod
    def _default_handle_newline     (self): ...

    @abc.abstractmethod
    def _default_handle_eof         (self): ...

class Parser(StackingSemiParser):

    def __init__                    (self, stream_handler:handlers.entity.Handler):

        super().__init__()
        self._NEXT                                                = stream_handler
        self._line             :str                         |None = None
        self._part             :str                               = ''
        self._class_name_stack :list[str]                         = list()
        # resettable state
        self._state                                               = state.States.DEFAULT
        self._package          :str                         |None = None
        self._static           :bool                              = False
        self._imported         :str                         |None = None
        self._access           :model.AccessModifier        |None = None
        self._finality         :model.FinalityType          |None = None
        self._synchronized     :bool                        |None = False
        self._volatile         :bool                        |None = False
        self._class_type       :model.ClassType             |None = None
        self._class_name       :str                         |None = None
        self._class_generics   :str                         |None = None
        self._class_subc       :dict[model.InheritanceType, list[model.Type]]\
                                                            |None = None
        self._class_subc_cur   :model.InheritanceType       |None = None
        self._attr_type        :model.Type                  |None = None
        self._attr_name        :str                         |None = None
        self._attr_value_parts :list[str]                   |None = None
        self._attr_nest_depth  :int                         |None = None
        self._attr_scope_depth :int                         |None = None
        self._sign             :dict[str,model.Argument]    |None = None
        self._sign_after       :typing.Callable[[dict[str,model.Argument]],None]\
                                                            |None = None
        self._constructor_sign :dict[str,model.Argument]    |None = None
        self._method_sign      :dict[str,model.Argument]    |None = None
        self._method_generics  :list[model.GenericType]     |None = None
        self._enumv_name       :str                         |None = None
        self._throws           :list[model.Type]            |None = None

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.DEFAULT

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_import               (self):

        self._NEXT.handle_import(model.Import(name  =self._imported,
                                              static=self._static))
        self._state = state.States.DEFAULT
        self._imported = None
        self._static   = False

    def _flush_package              (self):

        self._NEXT.handle_package(model.Package(name=self._package))
        self._state = state.States.DEFAULT
        self._package  = None

    def _flush_annotation           (self, annot:model.Annotation):

        self._NEXT.handle_annotation(annot)
        self._state = state.States.DEFAULT

    def _flush_class                (self):

        self._NEXT.handle_class(model.Class(name      =self._class_name, 
                                            generics  =self._class_generics,
                                            static    =self._static,
                                            access    =self._coerce_access(self._access),
                                            finality  =self._coerce_finality(self._finality),
                                            type      =self._class_type,
                                            subclass  =dict(self._class_subc)))
        self._class_name_stack.append(self._class_name)
        self._state          = state.States.DEFAULT if self._class_type is not model.ClassTypes.ENUM else \
                               state.States.ENUM
        self._class_name     = None
        self._class_generics = None
        self._static         = False
        self._access         = None
        self._finality       = None
        self._class_type     = None
        self._class_subc     = None

    def _flush_class_end            (self):

        self._NEXT.handle_class_end(model.ClassEnd())
        self._state = state.States.DEFAULT
        self._class_name_stack.pop()

    def _flush_static_constructor   (self, body:str): 
        
        self._NEXT.handle_static_constructor(model.StaticConstructor(body=body))
        self._state  = state.States.DEFAULT
        self._static = False

    def _flush_constructor          (self, body:str): 
        
        self._NEXT.handle_constructor(model.Constructor(access=self._coerce_access(self._access),
                                                        args  =self._constructor_sign, 
                                                        body  =body))
        self._state            = state.States.DEFAULT
        self._access           = None
        self._constructor_sign = None

    def _flush_attr                 (self, decl_only=False):

        self._NEXT.handle_attr(model.Attribute(name     =self._attr_name, 
                                               static   =self._static,
                                               volatile =self._volatile,
                                               final    =self._finality is model.FinalityTypes.FINAL,
                                               access   =self._coerce_access(self._access), 
                                               type     =self._attr_type,
                                               value    =None if decl_only else ''.join(self._attr_value_parts)))
        self._state = state.States.DEFAULT
        self._attr_name        = None
        self._static           = False
        self._volatile         = False
        self._finality         = None
        self._access           = None
        self._attr_type        = None

    def _flush_method               (self, body:str|None): 
        
        self._NEXT.handle_method(model.Method(name        =self._attr_name,
                                              static      =self._static,
                                              access      =self._coerce_access(self._access),
                                              finality    =self._coerce_finality(self._finality),
                                              synchronized=self._synchronized,
                                              generics    =self._method_generics,
                                              type        =self._attr_type,
                                              args        =self._method_sign,
                                              throws      =self._throws if self._throws is not None else list(),
                                              body        =body))
        self._state           = state.States.DEFAULT
        self._attr_name       = None
        self._static          = False
        self._synchronized    = False
        self._access          = None
        self._finality        = None
        self._method_generics = None
        self._attr_type       = None
        self._throws          = None
        self._method_sign     = None

    def _store_method_signature     (self, signature:dict[str,model.Argument]):

        self._state       = state.States.METHOD_DECLARED
        self._method_sign = signature

    def _flush_enumv                (self, callargs:list[str]|None=None):

        self._NEXT.handle_enum_value(model.EnumValue(name=self._enumv_name, 
                                                     args=callargs if callargs is not None else list()))
        self._state      = state.States.ENUM_DEFINED
        self._enumv_name = None

    def _store_class_name           (self, type:model.Type):

        self._class_name     = type.name
        self._class_generics = type.generics
        self._state          = state.States.CLASS_AFTER_NAME
        self._class_subc     = defaultdict(list)

    def _store_superclass           (self, type:model.Type): 
        
        line = self._line
        self._class_subc[self._class_subc_cur].append(type)
        self._state = state.States.CLASS_SUPERCLASS_NAMED

    def _store_constructor_declared (self, signature:dict[str,model.Argument]):

        self._state            = state.States.CONSTRUCTOR_DECLARED
        self._constructor_sign = signature

    def _store_attr_type            (self, type:model.Type):

        self._attr_type = type
        self._state     = state.States.DECL_1

    def _store_method_generics      (self, generics:list[model.GenericType]):

        self._method_generics = generics
        self._state = state.States.DEFAULT

    def _store_throws               (self, type:model.Type):

        self._throws.append(type)
        self._state = state.States.METHOD_THROWS_AFTER

    @typing.override
    def _default_handle_line        (self, line:str): pass

    @typing.override
    def _default_handle_part        (self, part:str): 
        
        self._part = part
        line = self._line
        if   self._state is state.States.DEFAULT:

            if   part == words.SEMICOLON  : pass

            elif part == words.CURLY_OPEN : 
                
                if self._static and (self._attr_type is None): 
                    
                    self._state = state.States.STATIC_CONSTRUCTOR_BODY
                    self._stack_handler(parsers.body.Parser(after=self._unstacking(self._flush_static_constructor)))
                    self.handle_part(part) # re-handle part ('{'), since it was used only for look-ahead
                    
                elif self._class_name is not None:

                    self._flush_class()

                else: raise exc.NotConstructorException(line)

            elif part == words.CURLY_CLOSE: 
                
                self._flush_class_end()

            elif part == words.IMPORT     : self._state = state.States.IMPORT

            elif part == words.PACKAGE    : self._state = state.States.PACKAGE

            elif part in _FINALITY_TYPE_KEYWORDS: 
                
                if self._finality is not None: raise exc.FinalityDuplicateException(line)
                self._finality = _FINALITY_TYPE_MAP_BY_KEYWORD[part]

            elif part in _ACCESS_MOD_KEYWORDS:

                if self._access is not None: raise exc.AccessModifierDuplicateException(line)
                self._access = _ACCESS_MOD_MAP_BY_KEYWORD[part]

            elif part in _CLASS_TYPE_KEYWORDS:

                if self._class_type is not None: raise exc.ClassException(line)
                self._class_type = _CLASS_TYPE_MAP_BY_KEYWORD[part]
                self._state      = state.States.CLASS_BEGIN
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_class_name), part_rehandler=self.handle_part, can_be_array=False))

            elif part == words.SYNCHRONIZED:

                if self._synchronized: raise exc.SynchronizedDuplicateException(line)
                self._synchronized = True

            elif part == words.VOLATILE:

                if self._volatile: raise exc.VolatileDuplicateException(line)
                self._volatile = True

            elif part == words.STATIC    :

                if self._static: raise exc.StaticDuplicateException(line)
                self._static = True

            elif part == words.ATSIGN    : 
                
                self._state = state.States.ANNOTATION
                self._stack_handler(parsers.annotation.Parser(after=self._unstacking(self._flush_annotation), part_rehandler=self.handle_part))
                self.handle_part(part)

            elif part == words.ANGLE_OPEN:

                if self._method_generics is not None: raise exc.GenericsDuplicateException(line)
                self._stack_handler(parsers.generics.Parser(after=self._unstacking(self._store_method_generics)))
                self.handle_part(part)

            else: 
                
                self._state = state.States.ATTR_BEGIN
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_attr_type), part_rehandler=self.handle_part))
                self.handle_part(part)

            return
        
        elif self._state is state.States.PACKAGE:

            if self._package is None: 

                self._package = part
            
            elif part == words.SEMICOLON:

                self._flush_package()

            elif part == words.DOT          or \
                 part == words.ASTERISK     or \
                 not words.is_reserved(part):

                self._package += part

            else: raise exc.PackageException(line)
            return
        
        elif self._state is state.States.IMPORT:

            if self._imported is None: 

                if part == words.STATIC: 
                    
                    self._static = True
                    return
                
                self._imported = part

            elif part == words.SEMICOLON:

                self._flush_import()
                return

            elif part == words.DOT          or \
                 part == words.ASTERISK     or \
                 not words.is_reserved(part):

                self._imported += part

            else: raise exc.ImportException(line)
            return
        
        elif self._state is state.States.CLASS_AFTER_NAME:

            if   part in _INHERIT_TYPE_KEYWORDS:

                it = _INHERIT_TYPE_MAP_BY_KEYWORD[part]
                if it in self._class_subc: raise exc.ClassException(line) # repeated extends or implements
                self._state          = state.States.CLASS_SUPERCLASS
                self._class_subc_cur = it
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_superclass), part_rehandler=self.handle_part, can_be_array=False))

            elif part == words.CURLY_OPEN:

                self._flush_class()

            else: raise exc.ClassException(line)
            return

        elif self._state is state.States.CLASS_SUPERCLASS_NAMED:

            if   part == words.COMMA:

                self._state = state.States.CLASS_SUPERCLASS_SEP

            elif part == words.CURLY_OPEN:

                self._flush_class()

            elif part in _INHERIT_TYPE_KEYWORDS: 
                
                self._state = state.States.CLASS_AFTER_NAME
                self.handle_part(part)

            else: raise exc.ClassException(line)
            return
        
        elif self._state is state.States.CLASS_SUPERCLASS_SEP:

            self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_superclass), part_rehandler=self.handle_part, can_be_array=False))
            self.handle_part(part)
            return

        elif self._state is state.States.DECL_1:

            if part == words.PARENTH_OPEN:
                
                if (self._attr_type.name == self._class_name_stack[-1]): # constructor, since previously we got a word equal to the class' name

                    self._state = state.States.CONSTRUCTOR_SIGNATURE
                    self._stack_handler(parsers.signature.Parser(after=self._unstacking(self._store_constructor_declared)))
                    self.handle_part(part) # re-handle part ('('), since it was used only for look-ahead

                else:

                    raise exc.MethodException(line)

            else:

                self._attr_name  = part
                self._state = state.States.DECL_2

            return
        
        elif self._state is state.States.DECL_2:

            if   part == words.SEMICOLON:

                self._flush_attr(decl_only=True)
            
            elif part == words.EQUALSIGN:

                self._state = state.States.ATTR_INITIALIZE
                self._attr_value_parts = list()
                self._attr_nest_depth  = 0
                self._attr_scope_depth = 0
            
            elif part == words.PARENTH_OPEN:

                self._state = state.States.METHOD_SIGNATURE
                self._stack_handler(parsers.signature.Parser(after=self._unstacking(self._store_method_signature)))
                self.handle_part(part) # re-handle part ('('), since it was used only for look-ahead

            else: raise exc.AttributeException(line)
            return
            
        elif self._state is state.States.CONSTRUCTOR_DECLARED:

            self._state = state.States.CONSTRUCTOR_BODY
            self._stack_handler(parsers.body.Parser(after=self._unstacking(self._flush_constructor)))
            self.handle_part(part) # re-handle part ('{'), since it was used only for look-ahead
            return

        elif self._state is state.States.ATTR_INITIALIZE:

            if self._attr_nest_depth  == 0 and \
               self._attr_scope_depth == 0 and \
               part                   == words.SEMICOLON: 
                
                self._flush_attr()
                self._attr_nest_depth  = None
                self._attr_scope_depth = None
                return

            else:

                self._attr_value_parts.append(part)
                if   part == words.CURLY_OPEN   : self._attr_scope_depth += 1
                elif part == words.CURLY_CLOSE  : self._attr_scope_depth -= 1
                elif part == words.PARENTH_OPEN : self._attr_nest_depth  += 1
                elif part == words.PARENTH_CLOSE: self._attr_nest_depth  -= 1
                return

        elif self._state is state.States.METHOD_DECLARED:

            if   part == words.SEMICOLON:

                self._flush_method(body=None)
            
            elif part == words.THROWS:

                if self._throws is not None: raise exc.MethodException(line)
                self._state  = state.States.METHOD_THROWS
                self._throws = list()
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_throws), part_rehandler=self.handle_part, can_be_array=False))

            else:

                self._state = state.States.METHOD_BODY
                self._stack_handler(parsers.body.Parser(after=self._unstacking(self._flush_method)))
                self.handle_part(part) # re-handle part ('{'), since it was used only for look-ahead

            return
        
        elif self._state is state.States.METHOD_THROWS_AFTER:

            if part == words.COMMA:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_throws), part_rehandler=self.handle_part, can_be_array=False))

            else:

                self._state = state.States.METHOD_DECLARED
                self.handle_part(part)

            return

        elif self._state is state.States.ENUM:

            if   part == words.SEMICOLON:

                self._state = state.States.DEFAULT

            if   part == words.CURLY_CLOSE:

                self._state = state.States.DEFAULT
                self.handle_part(part)

            elif not _WORD_PATTERN.match(part):

                raise exc.EnumValueException(line)
            
            else:

                self._enumv_name = part
                self._state = state.States.ENUM_NAMED

            return

        elif self._state is state.States.ENUM_NAMED:

            if   part in {words.SEMICOLON,
                          words.COMMA,
                          words.CURLY_CLOSE}:

                self._flush_enumv()
                self.handle_part(part) # re-handle part (either semicolon or comma), as it was used only for look-ahead

            else:
                
                self._stack_handler(parsers.callargs.Parser(after=self._unstacking(self._flush_enumv)))
                self.handle_part(part) # re-handle part ('('), since it was used only for look-ahead

            return

        elif self._state is state.States.ENUM_DEFINED:

            if part == words.SEMICOLON:

                self._state = state.States.DEFAULT

            elif part is words.CURLY_CLOSE:

                self._state = state.States.DEFAULT
                self.handle_part(part)

            elif part is words.COMMA:

                self._state = state.States.ENUM

            else: raise exc.EnumValueException(line)
            return

        raise NotImplementedError(f'{line} (state = {self._state.name})')
        
    @typing.override
    def _default_handle_comment     (self, text:str):

        self._NEXT.handle_comment(comment=model.Comment(text=text))

    @typing.override
    def _default_handle_spacing     (self, spacing:str):

        if self._state is state.States.ATTR_INITIALIZE:

            self._attr_value_parts.append(spacing)

        else: pass

    @typing.override
    def _default_handle_newline     (self):

        self.handle_spacing(spacing='\n')

    @typing.override
    def _default_handle_eof         (self):
        
        line = self._line
        if self._state            != state.States.DEFAULT or \
           self._class_name_stack                        : raise exc.EOFException(line)
