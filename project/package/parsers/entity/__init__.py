DEBUG = 0

import abc
from   collections import defaultdict
import dataclasses
import re
import typing

from .            import exc, state
from ...          import handlers, model, util, words, parsers

from jl95terceira.batteries import ChainedCallables

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
        self._line      :str                  |None = None
        self._part      :str                  |None = None

    def _stack_handler              (self, handler:handlers.part.Handler):

        self._subhandler = handler
        self._subhandler.handle_line(self._line)

    def _unstack_handler            (self):

        self._subhandler = None

    def _unstacking                 (self, f): return ChainedCallables(lambda *a, **ka: self._unstack_handler(), f)

    @typing.override
    def handle_line                 (self, line:str):

        self._line = line
        if self._subhandler is not None: self._subhandler.handle_line(line)
        else                           : self.   _default_handle_line(line)

    @typing.override
    def handle_part                 (self, part:str): 
        if DEBUG: print(part)
        self._part = part
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
        self._default_handle_eof()

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

class ParserResettableVariables:

    def __init__(self):

        self.state                                                = state.States.DEFAULT
        self.static           :bool                               = False
        self.default          :bool                               = False
        self.access           :model.AccessModifier         |None = None
        self.finality         :model.FinalityType           |None = None
        self.synchronized                                         = False
        self.volatile                                             = False
        self.transient        :bool                               = False
        self.annotations      :list[model.Annotation]             = list()
        self.class_type       :model.ClassType              |None = None
        self.class_name       :str                          |None = None
        self.class_generics   :str                          |None = None
        self.class_subc       :dict[model.InheritanceType, list[model.Type]]\
                                                                  = defaultdict(list)
        self.class_subc_cur   :model.InheritanceType        |None = None
        self.attr_type        :model.Type                   |None = None
        self.attr_name        :str                          |None = None
        self.attr_value_parts :list[str]                    |None = None
        self.attr_nest_depth  :int                          |None = None
        self.attr_scope_depth :int                          |None = None
        self.method_signature      :dict[str,model.Argument]|None = None
        self.method_generics  :list[model.GenericType]      |None = None
        self.method_defaultv  :str                          |None = None
        self.enumv_name       :str                          |None = None
        self.enumv_subclasses                                     = False
        self.throws           :list[model.Type]             |None = None

@dataclasses.dataclass
class ParserClassStackElement:

    class_        :model.Class|None = dataclasses.field()
    in_enum_values:bool             = dataclasses.field(default=False)

class Parser(StackingSemiParser):

    def __init__                    (self, stream_handler:handlers.entity.Handler):

        super().__init__()
        self._NEXT                                      = stream_handler
        self._vars                                      = ParserResettableVariables()
        self._class_stack:list[ParserClassStackElement] = list()

    def _reset_vars(self, state:state.State|None=None):

        self._vars = ParserResettableVariables()
        if state is not None:

            self._vars.state = state

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.DEFAULT

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_class                (self):

        class_ = model.Class(name       =self._vars.class_name, 
                             annotations=self._vars.annotations,
                             generics   =self._vars.class_generics,
                             static     =self._vars.static,
                             access     =self._coerce_access(self._vars.access),
                             finality   =self._coerce_finality(self._vars.finality),
                             type       =self._vars.class_type,
                             inherit    =dict(self._vars.class_subc),
                             signature  =self._vars.method_signature)
        self._NEXT.handle_class(class_)
        self._class_stack.append(ParserClassStackElement(class_        =class_, 
                                                         in_enum_values=self._vars.class_type is model.ClassTypes.ENUM))
        self._reset_vars(state=state.States.DEFAULT if self._vars.class_type is not model.ClassTypes.ENUM else \
                               state.States.ENUM)

    def _flush_class_end            (self):

        self._NEXT.handle_class_end()
        self._class_stack.pop()
        if self._class_stack and self._class_stack[-1].in_enum_values:
            
            self._vars.state = state.States.ENUM_DEFINED

    def _flush_initializer          (self, body:str): 
        
        self._NEXT.handle_initializer(model.Initializer(body  =body,
                                                        static=self._vars.static))
        self._reset_vars()

    def _flush_constructor          (self, body:str): 
        
        self._NEXT.handle_constructor(model.Constructor(access=self._coerce_access(self._vars.access),
                                                        args  =self._vars.method_signature, 
                                                        body  =body,
                                                        throws=self._vars.throws if self._vars.throws is not None else list()))
        self._reset_vars()

    def _flush_attribute            (self, decl_only=False,
                                           continued=False):

        self._NEXT.handle_attr(model.Attribute(name     =self._vars.attr_name, 
                                               type     =self._vars.attr_type,
                                               static   =self._vars.static,
                                               volatile =self._vars.volatile,
                                               final    =self._vars.finality is model.FinalityTypes.FINAL,
                                               access   =self._coerce_access(self._vars.access), 
                                               transient=self._vars.transient,
                                               value    =None if decl_only else ''.join(self._vars.attr_value_parts)))
        if continued: return
        self._reset_vars()

    def _flush_method               (self, body:str|None): 
        
        self._NEXT.handle_method(model.Method(name         =self._vars.attr_name,
                                              static       =self._vars.static,
                                              default      =self._vars.default,
                                              access       =self._coerce_access(self._vars.access),
                                              finality     =self._coerce_finality(self._vars.finality),
                                              synchronized =self._vars.synchronized,
                                              generics     =self._vars.method_generics,
                                              type         =self._vars.attr_type,
                                              args         =self._vars.method_signature,
                                              throws       =self._vars.throws if self._vars.throws is not None else list(),
                                              default_value=self._vars.method_defaultv,
                                              body         =body))
        self._reset_vars()

    def _flush_enum_value           (self, callargs:list[str]|None=None):

        self._NEXT.handle_enum_value(model.EnumValue(name      =self._vars.enumv_name, 
                                                     args      =callargs if callargs is not None else list(),
                                                     subclasses=self._vars.enumv_subclasses))
        subclasses = self._vars.enumv_subclasses
        self._reset_vars()
        if not subclasses: 
            
            self._vars.state = state.States.ENUM_DEFINED

        else: 
            
            self._class_stack.append(ParserClassStackElement(class_=None))

    def _store_annotation           (self, annotation: model.Annotation):

        if annotation.name == words.INTERFACE: 
            
            if annotation.args: raise exc.Exception(self._line)
            self._vars.state = state.States.AINTERFACE

        else:

            self._vars.annotations.append(annotation)

    def _store_method_signature     (self, signature:dict[str,model.Argument]):

        self._vars.state       = state.States.METHOD_DECLARED
        self._vars.method_signature = signature

    def _store_class_name           (self, type:model.Type):

        self._vars.class_name     = type.name
        self._vars.class_generics = type.generics
        self._vars.state          = state.States.CLASS_AFTER_NAME
        self._vars.class_subc     = defaultdict(list)

    def _store_record_name          (self, type:model.Type):

        self._vars.class_name     = type.name
        self._vars.class_generics = type.generics
        self._vars.state          = state.States.RECORD_AFTER_NAME
        self._stack_handler(parsers.signature.Parser(after=self._unstacking(self._store_record_signature)))

    def _store_record_signature     (self, signature:dict[model.Argument]):

        self._vars.method_signature = signature
        self._vars.state       = state.States.CLASS_AFTER_NAME

    def _store_superclass           (self, type:model.Type): 
        
        line = self._line
        self._vars.class_subc[self._vars.class_subc_cur].append(type)
        self._vars.state = state.States.CLASS_SUPERCLASS_NAMED

    def _store_constructor_signature(self, signature:dict[str,model.Argument]):

        self._vars.state            = state.States.CONSTRUCTOR_DECLARED
        self._vars.method_signature = signature

    def _store_constructor_throws   (self, type:model.Type):

        self._vars.throws.append(type)
        self._vars.state = state.States.CONSTRUCTOR_THROWS_AFTER

    def _store_attribute_type       (self, type:model.Type):

        self._vars.attr_type = type
        self._vars.state     = state.States.LOOKAHEAD_1

    def _store_attribute_name       (self, name:str): 
        
        self._vars.attr_name  = name
        self._vars.state      = state.States.LOOKAHEAD_2

    def _if_array_after_attr_name   (self, dim:int): 
        
        self._vars.attr_type.array_dim += dim

    def _store_method_generics      (self, generics:list[model.GenericType]):

        self._vars.method_generics = generics
        self._vars.state = state.States.DEFAULT

    def _store_method_throws        (self, type:model.Type):

        self._vars.throws.append(type)
        self._vars.state = state.States.METHOD_THROWS_AFTER

    def _store_method_default_value (self, value:str):

        self._vars.method_defaultv = value
        self._vars.state = state.States.METHOD_DEFAULT_VALUE_AFTER

    @typing.override
    def _default_handle_line        (self, line:str): pass

    @typing.override
    def _default_handle_part        (self, part:str): 
        
        self._part = part
        line = self._line
        if   self._vars.state is state.States.DEFAULT:

            if   part == words.SEMICOLON: pass

            elif part == words.CURLY_OPEN: 
                
                if self._vars.attr_type is None: 
                    
                    self._vars.state = state.States.INITIALIZER_BODY
                    self._stack_handler(parsers.body.Parser(after=self._unstacking(self._flush_initializer), skip_begin=True))
                    
                elif self._vars.class_name is not None:

                    self._flush_class()

                else: raise exc.NotConstructorException(line)

            elif part == words.CURLY_CLOSE: 
                
                self._flush_class_end()

            elif part == words.IMPORT: 
                
                self._stack_handler(parsers.import_.Parser(after=self._unstacking(self._NEXT.handle_import), skip_begin=True))

            elif part == words.PACKAGE: 
                
                self._stack_handler(parsers.package.Parser(after=self._unstacking(self._NEXT.handle_package), skip_begin=True))

            elif part == words.DEFAULT:

                if self._vars.default: raise exc.DefaultDuplicateException(line)
                self._vars.default = True

            elif part in _FINALITY_TYPE_KEYWORDS: 
                
                if self._vars.finality is not None: raise exc.FinalityDuplicateException(line)
                self._vars.finality = _FINALITY_TYPE_MAP_BY_KEYWORD[part]

            elif part in _ACCESS_MOD_KEYWORDS:

                if self._vars.access is not None: raise exc.AccessModifierDuplicateException(line)
                self._vars.access = _ACCESS_MOD_MAP_BY_KEYWORD[part]

            elif part in _CLASS_TYPE_KEYWORDS:

                if self._vars.class_type is not None: raise exc.ClassException(line)
                self._vars.class_type = _CLASS_TYPE_MAP_BY_KEYWORD[part]
                self._vars.state      = state.States.CLASS
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_class_name), part_rehandler=self.handle_part, allow_array=False))

            elif part == words.RECORD:

                self._vars.state = state.States.RECORD
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_record_name), part_rehandler=self.handle_part, allow_array=False))

            elif part == words.SYNCHRONIZED:

                if self._vars.synchronized: raise exc.SynchronizedDuplicateException(line)
                self._vars.synchronized = True

            elif part == words.VOLATILE:

                if self._vars.volatile: raise exc.VolatileDuplicateException(line)
                self._vars.volatile = True

            elif part == words.TRANSIENT: 
                
                if self._vars.transient: raise exc.TransientDuplicateException(line)
                self._vars.transient = True

            elif part == words.STATIC:

                if self._vars.static: raise exc.StaticDuplicateException(line)
                self._vars.static = True

            elif part == words.ATSIGN: 
                
                self._stack_handler(parsers.annotation.Parser(after=self._unstacking(self._store_annotation), part_rehandler=self.handle_part, skip_begin=True))

            elif part == words.ANGLE_OPEN:

                if self._vars.method_generics is not None: raise exc.GenericsDuplicateException(line)
                self._stack_handler(parsers.generics.Parser(after=self._unstacking(self._store_method_generics), skip_begin=True))

            else: 
                
                self._vars.state = state.States.ATTR_BEGIN
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_attribute_type), part_rehandler=self.handle_part))
                self.handle_part(part)

            return
        
        elif self._vars.state is state.States.CLASS_AFTER_NAME:

            if   part in _INHERIT_TYPE_KEYWORDS:

                it = _INHERIT_TYPE_MAP_BY_KEYWORD[part]
                if it in self._vars.class_subc: raise exc.ClassException(line) # repeated extends or implements
                self._vars.state          = state.States.CLASS_SUPERCLASS
                self._vars.class_subc_cur = it
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_superclass), part_rehandler=self.handle_part, allow_array=False))

            elif part == words.CURLY_OPEN:

                self._flush_class()

            else: raise exc.ClassException(line)
            return

        elif self._vars.state is state.States.CLASS_SUPERCLASS_NAMED:

            if   part == words.COMMA:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_superclass), part_rehandler=self.handle_part, allow_array=False))

            elif part == words.CURLY_OPEN:

                self._flush_class()

            elif part in _INHERIT_TYPE_KEYWORDS: 
                
                self._vars.state = state.States.CLASS_AFTER_NAME
                self.handle_part(part)

            else: raise exc.ClassException(line)
            return
        
        elif self._vars.state is state.States.LOOKAHEAD_1:

            if part == words.PARENTH_OPEN:
                
                parent_class = self._class_stack[-1].class_
                if (parent_class              is not None              and \
                    self._vars.attr_type.name ==     parent_class.name): # constructor, since previously we got a word equal to the class' name

                    self._vars.state = state.States.CONSTRUCTOR_SIGNATURE
                    self._stack_handler(parsers.signature.Parser(after=self._unstacking(self._store_constructor_signature), skip_begin=True))

                else: raise exc.MethodException(line)

            else:

                self._stack_handler(parsers.name.Parser(after=self._unstacking(self._store_attribute_name), part_rehandler=self.handle_part, if_array=self._if_array_after_attr_name))
                self.handle_part(part)

            return
        
        elif self._vars.state is state.States.LOOKAHEAD_2:

            if   part == words.SEMICOLON:

                self._flush_attribute(decl_only=True)
            
            elif part == words.COMMA:

                self._flush_attribute(decl_only=True, continued=True)
                self._vars.state = state.States.ATTR_MULTI_SEP

            elif part == words.EQUALSIGN:

                self._vars.state            = state.States.ATTR_INITIALIZE
                self._vars.attr_value_parts = list()
                self._vars.attr_nest_depth  = 0
                self._vars.attr_scope_depth = 0
            
            elif part == words.PARENTH_OPEN:

                self._vars.state = state.States.METHOD_SIGNATURE
                self._stack_handler(parsers.signature.Parser(after=self._unstacking(self._store_method_signature)))
                self.handle_part(part) # re-handle part ('('), since it was used only for look-ahead

            else: raise exc.AttributeException(line)
            return
            
        elif self._vars.state is state.States.CONSTRUCTOR_DECLARED:

            if part == words.THROWS:

                if self._vars.throws is not None: raise exc.ThrowsDuplicateException(line)
                self._vars.state  = state.States.CONSTRUCTOR_THROWS
                self._vars.throws = list()
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_constructor_throws), part_rehandler=self.handle_part, allow_array=False))

            else:

                self._vars.state = state.States.CONSTRUCTOR_BODY
                self._stack_handler(parsers.body.Parser(after=self._unstacking(self._flush_constructor)))
                self.handle_part(part) # re-handle part ('{'), since it was used only for look-ahead
            
            return

        elif self._vars.state is state.States.ATTR_MULTI_SEP:

            if not _WORD_PATTERN.match(part): raise exc.AttributeException(line)
            self._vars.attr_name = part
            self._vars.state = state.States.ATTR_MULTI
            return

        elif self._vars.state is state.States.ATTR_MULTI:

            if   part == words.SEMICOLON:

                self._flush_attribute(decl_only=True)
            
            elif part == words.COMMA:

                self._flush_attribute(decl_only=True, continued=True)
                self._vars.state = state.States.ATTR_MULTI_SEP

            else: raise exc.AttributeException(line)
            return

        elif self._vars.state is state.States.CONSTRUCTOR_THROWS_AFTER:

            if part == words.COMMA:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_constructor_throws), part_rehandler=self.handle_part, allow_array=False))

            else:

                self._vars.state = state.States.CONSTRUCTOR_DECLARED
                self.handle_part(part)

            return

        elif self._vars.state is state.States.ATTR_INITIALIZE:

            if self._vars.attr_nest_depth  == 0 and \
               self._vars.attr_scope_depth == 0 and \
               part                   == words.SEMICOLON: 
                
                self._flush_attribute()
                self._vars.attr_nest_depth  = None
                self._vars.attr_scope_depth = None
                return

            else:

                self._vars.attr_value_parts.append(part)
                if   part == words.CURLY_OPEN   : self._vars.attr_scope_depth += 1
                elif part == words.CURLY_CLOSE  : self._vars.attr_scope_depth -= 1
                elif part == words.PARENTH_OPEN : self._vars.attr_nest_depth  += 1
                elif part == words.PARENTH_CLOSE: self._vars.attr_nest_depth  -= 1
                return

        elif self._vars.state is state.States.METHOD_DECLARED:

            if   part == words.SEMICOLON:

                self._flush_method(body=None)
            
            elif part == words.THROWS:

                if self._vars.throws is not None: raise exc.ThrowsDuplicateException(line)
                self._vars.state  = state.States.METHOD_THROWS
                self._vars.throws = list()
                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_method_throws), part_rehandler=self.handle_part, allow_array=False))

            elif part == words.DEFAULT:

                self._vars.state = state.States.METHOD_DEFAULT_VALUE

            elif part == words.CURLY_OPEN:

                self._vars.state = state.States.METHOD_BODY
                self._stack_handler(parsers.body.Parser(after=self._unstacking(self._flush_method)))
                self.handle_part(part) # re-handle part ('{'), since it was used only for look-ahead

            else: raise exc.MethodException(line)
            return
        
        elif self._vars.state is state.States.METHOD_DEFAULT_VALUE:

            self._stack_handler(parsers.expr.raw.Parser(after=self._unstacking(self._store_method_default_value), part_rehandler=self.handle_part))
            return

        elif self._vars.state is state.States.METHOD_DEFAULT_VALUE_AFTER:

            self._flush_method(None)
            return

        elif self._vars.state is state.States.METHOD_THROWS_AFTER:

            if part == words.COMMA:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_method_throws), part_rehandler=self.handle_part, allow_array=False))

            else:

                self._vars.state = state.States.METHOD_DECLARED
                self.handle_part(part)

            return

        elif self._vars.state is state.States.ENUM:

            if   part == words.SEMICOLON:

                self._vars.state = state.States.DEFAULT
                self._class_stack[-1].in_enum_values = False

            elif part == words.CURLY_CLOSE:

                self._vars.state = state.States.DEFAULT
                self.handle_part(part)

            elif part == words.ATSIGN:

                self._stack_handler(parsers.annotation.Parser(after=self._unstacking(self._vars.annotations.append), part_rehandler=self.handle_part, skip_begin=True))

            elif not _WORD_PATTERN.match(part):

                raise exc.EnumValueNameException(line)
            
            else:

                self._vars.enumv_name = part
                self._vars.state      = state.States.ENUM_NAMED

            return

        elif self._vars.state is state.States.ENUM_NAMED:

            if part == words.PARENTH_OPEN:
                
                self._stack_handler(parsers.callargs.Parser(after=self._unstacking(self._flush_enum_value)))
                self.handle_part(part) # re-handle part ('('), since it was used only for look-ahead

            else:

                self._flush_enum_value()
                self.handle_part(part) # re-handle part (either semicolon or comma), as it was used only for look-ahead

            return

        elif self._vars.state is state.States.ENUM_DEFINED:

            if   part == words.CURLY_OPEN:

                self._vars.enumv_subclasses = True
                self._flush_enum_value()

            else:

                self._vars.state = state.States.ENUM
                if part != words.COMMA:

                    self.handle_part(part)

            return

        elif self._vars.state is state.States.AINTERFACE:

            self._vars.class_name = part
            self._vars.state = state.States.AINTERFACE_NAMED
            return

        elif self._vars.state is state.States.AINTERFACE_NAMED:

            if part != words.CURLY_OPEN: raise exc.Exception(line)
            self._NEXT.handle_ainterface(model.AInterface(name       =self._vars.class_name,
                                                          access     =self._vars.access,
                                                          annotations=self._vars.annotations))
            self._class_stack.append(ParserClassStackElement(class_=None))
            self._reset_vars()
            return

        raise NotImplementedError(f'line = {repr(line)}, state = {repr(self._vars.state.name)}')
        
    @typing.override
    def _default_handle_comment     (self, text:str):

        self._NEXT.handle_comment(comment=model.Comment(text=text))

    @typing.override
    def _default_handle_spacing     (self, spacing:str):

        if self._vars.state is state.States.ATTR_INITIALIZE:

            self._vars.attr_value_parts.append(spacing)

        else: pass

    @typing.override
    def _default_handle_newline     (self):

        self.handle_spacing(spacing='\n')

    @typing.override
    def _default_handle_eof         (self):
        
        line = self._line
        if self._vars.state  != state.States.DEFAULT or \
           self._class_stack                        : raise exc.EOFException(line)
