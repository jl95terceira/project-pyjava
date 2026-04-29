DEBUG = 0

import abc
from   collections import defaultdict
from   dataclasses import dataclass, field
import re
import typing

from .       import exc, state
from ..util import *
from ...     import handlers, model, util, words, parsers

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
                                words.RECORD    :model.ClassTypes.RECORD,
                                words.ENUM      :model.ClassTypes.ENUM,}
_CLASS_TYPE_KEYWORDS         = set(_CLASS_TYPE_MAP_BY_KEYWORD)
_WORD_PATTERN                = re.compile('^\\w+$')

class _ParserResettableVariables:

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
        self.method_signature :dict[str,model.Argument]     |None = None
        self.method_generics  :list[model.GenericType]      |None = None
        self.method_defaultv  :str                          |None = None
        self.enumv_name       :str                          |None = None
        self.enumv_args   :list[str]                    |None = None
        self.throws           :list[model.Type]             |None = None

@dataclass
class _ParserClassStackElement:

    class_ :handlers.decl.ClassHeaderDeclaration|None = field()
    vars   :_ParserResettableVariables                 = field()
    in_enum:bool                                      = field(default=False)

class Parser(StackingSemiParser):

    def __init__                    (self, stream_handler:handlers.entity.Handler):

        super().__init__()
        self._NEXT                                      = stream_handler
        self._vars                                      = _ParserResettableVariables()
        self._class_stack:list[_ParserClassStackElement] = list()

    def _reset_vars(self, state:state.State|None=None):

        self._vars = _ParserResettableVariables()
        if state is not None:

            self._vars.state = state

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.DEFAULT

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_class                (self):

        class_ = handlers.decl.ClassHeaderDeclaration(
            name  =self._vars.class_name, 
            static=self._vars.static,
            header=model.InterfaceHeader(
                annotations=self._vars.annotations,
                generics   =self._vars.class_generics,
                access     =self._coerce_access(self._vars.access),
                inherit    =list(self._vars.class_subc[model.InheritanceTypes.IMPLEMENTS])
            ) if self._vars.class_type is model.ClassTypes.INTERFACE else \
                   model.RecordHeader(
                annotations=self._vars.annotations,
                generics   =self._vars.class_generics,
                access     =self._coerce_access(self._vars.access),
                finality   =self._coerce_finality(self._vars.finality),
                inherit    =defaultdict(list, self._vars.class_subc),
                signature  =self._vars.method_signature
            ) if self._vars.class_type is model.ClassTypes.RECORD else \
                   model.AInterfaceHeader(
                annotations=self._vars.annotations,
                access     =self._coerce_access(self._vars.access)
            ) if self._vars.class_type is model.ClassTypes.AINTERFACE else \
                   model.AbstractClassHeader(
                annotations=self._vars.annotations,
                generics   =self._vars.class_generics,
                access     =self._coerce_access(self._vars.access),
                inherit    =defaultdict(list, self._vars.class_subc),
            ) if self._vars.finality is model.FinalityTypes.ABSTRACT else \
                   model.ConcreteClassHeader(
                annotations=self._vars.annotations,
                generics   =self._vars.class_generics,
                access     =self._coerce_access(self._vars.access),
                finality   =self._coerce_finality(self._vars.finality),
                inherit    =defaultdict(list, self._vars.class_subc),
            )
        )
        self._NEXT.handle_class(class_)
        self._class_stack.append(_ParserClassStackElement(class_ =class_, 
                                                          vars   =self._vars,
                                                          in_enum=self._vars.class_type is model.ClassTypes.ENUM))
        self._reset_vars(state=state.States.DEFAULT if self._vars.class_type is not model.ClassTypes.ENUM else \
                               state.States.ENUM)

    def _flush_class_end            (self):
        
        self._NEXT.handle_class_end()
        self._class_stack.pop()
        self._reset_vars() 
        if self._class_stack and self._class_stack[-1].vars.class_type is model.ClassTypes.ENUM and self._class_stack[-1].in_enum:
            
            self._vars.state = state.States.ENUM_DEFINED

    def _flush_initializer          (self, body:str): 
        
        self._NEXT.handle_initializer(handlers.decl.InitializerDeclaration(static     =self._vars.static, 
                                                                             initializer=model.Initializer(body=body)))
        self._reset_vars()

    def _flush_constructor          (self, body:str): 
        
        self._NEXT.handle_constructor(handlers.decl.ConstructorDeclaration(model.Constructor(access=self._coerce_access(self._vars.access),
                                                                                               args  =self._vars.method_signature, 
                                                                                               body  =body,
                                                                                               throws=self._vars.throws if self._vars.throws is not None else list())))
        self._reset_vars()

    def _flush_attribute            (self, decl_only=False,
                                           continued=False):

        self._NEXT.handle_attribute(handlers.decl.AttributeDeclaration(name     =self._vars.attr_name, 
                                                                         static   =self._vars.static,
                                                                         attribute=model.Attribute(type     =self._vars.attr_type,
                                                                                                   volatile =self._vars.volatile,
                                                                                                   final    =self._vars.finality is model.FinalityTypes.FINAL,
                                                                                                   access   =self._coerce_access(self._vars.access), 
                                                                                                   transient=self._vars.transient,
                                                                                                   value    =None if decl_only else ''.join(self._vars.attr_value_parts))))
        if continued: return
        self._reset_vars()

    def _flush_method               (self, body:str|None): 
        
        parent_class_decl = (lambda e: e.class_)(self._class_stack[-1])
        assert self._vars.attr_name        is not None
        assert self._vars.method_signature is not None
        self._NEXT.handle_method(handlers.decl.MethodDeclaration(
            name  =self._vars.attr_name,
            static=self._vars.static,
            method=model.AInterfaceMethod(
                type         =self._vars.attr_type,
                default_value=self._vars.method_defaultv
            ) if parent_class_decl is not None and isinstance(parent_class_decl.header, model.AInterfaceHeader) else \
                   model.AbstractMethod(
                type        =self._vars.attr_type,
                access      =self._coerce_access(self._vars.access),
                synchronized=self._vars.synchronized,
                generics    =self._vars.method_generics,
                args        =self._vars.method_signature,
                throws      =self._vars.throws if self._vars.throws is not None else list()
            ) if self._vars.finality is model.FinalityTypes.ABSTRACT else \
                   model.ConcreteMethod(
                access       =self._coerce_access(self._vars.access),
                finality     =self._coerce_finality(self._vars.finality),
                synchronized =self._vars.synchronized,
                generics     =self._vars.method_generics,
                type         =self._vars.attr_type,
                args         =self._vars.method_signature,
                throws       =self._vars.throws if self._vars.throws is not None else list(),
                body         =body
            ) if self._vars.finality is not model.FinalityTypes.DEFAULT and body is not None else \
                   model.InterfaceMethod(
                type         =self._vars.attr_type,
                generics     =self._vars.method_generics,
                args         =self._vars.method_signature,
                throws       =self._vars.throws if self._vars.throws is not None else list(),
            ) if self._vars.finality is not model.FinalityTypes.DEFAULT else \
                   model.InterfaceDefaultMethod(
                type         =self._vars.attr_type,
                generics     =self._vars.method_generics,
                args         =self._vars.method_signature,
                throws       =self._vars.throws if self._vars.throws is not None else list(),
                body         =body
            )
        ))
        self._reset_vars()

    def _flush_enum_value           (self):

        self._NEXT.handle_enum_value(handlers.decl.EnumValueDeclaration(name     =self._vars.enumv_name, 
                                                                          enumvalue=model.EnumValue(args       =self._vars.enumv_args,
                                                                                                    annotations=self._vars.annotations)))
        self._reset_vars()
        self._vars.state = state.States.ENUM_DEFINED        

    def _store_annotation           (self, annotation: model.Annotation):

        if annotation.name == words.INTERFACE: 
            
            if annotation.args: raise exc.Exception(self._line)
            self._vars.class_type = model.ClassTypes.AINTERFACE
            self._vars.state      = state.States.CLASS
            self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_class_name), token_rehandler=self.handle_token, allow_array=False))

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
        self._stack_handler(parsers.signature.Parser(signature_handler=self._unstacking(self._store_record_signature)))

    def _store_record_signature     (self, signature:dict[str,model.Argument]):

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

    def _store_enumvalue_args   (self, args:list[str]): 
        
        self._vars.enumv_args = args
        self._vars.state          = state.States.ENUM_AFTER_CALLARGS

    @typing.override
    def _default_handle_line        (self, line:str): pass

    @typing.override
    def _default_handle_token       (self, token:str): 
        
        if DEBUG: print(f'    {self._vars.state}')
        self._part = token
        line = self._line
        if   self._vars.state is state.States.DEFAULT:

            if   token == words.SEMICOLON: pass

            elif token == words.CURLY_OPEN: 
                
                if self._vars.attr_type is None: 
                    
                    self._vars.state = state.States.INITIALIZER_BODY
                    self._stack_handler(parsers.body.Parser(body_handler=self._unstacking(self._flush_initializer), skip_begin=True))
                    
                elif self._vars.class_name is not None:

                    self._flush_class()

                else: raise exc.NotConstructorException(line)

            elif token == words.CURLY_CLOSE: 
                
                self._flush_class_end()

            elif token == words.IMPORT: 
                
                self._stack_handler(parsers.import_.Parser(import_handler=self._unstacking(self._NEXT.handle_import), skip_begin=True))

            elif token == words.PACKAGE: 
                
                self._stack_handler(parsers.package.Parser(package_handler=self._unstacking(self._NEXT.handle_package), skip_begin=True))

            elif token == words.DEFAULT:

                if self._vars.default: raise exc.DefaultDuplicateException(line)
                self._vars.default = True

            elif token in _FINALITY_TYPE_KEYWORDS: 
                
                if self._vars.finality is not None: raise exc.FinalityDuplicateException(line)
                self._vars.finality = _FINALITY_TYPE_MAP_BY_KEYWORD[token]

            elif token in _ACCESS_MOD_KEYWORDS:

                if self._vars.access is not None: raise exc.AccessModifierDuplicateException(line)
                self._vars.access = _ACCESS_MOD_MAP_BY_KEYWORD[token]

            elif token in _CLASS_TYPE_KEYWORDS:

                if self._vars.class_type is not None: raise exc.ClassException(line)
                self._vars.class_type = _CLASS_TYPE_MAP_BY_KEYWORD[token]
                if token != words.RECORD:

                    self._vars.state = state.States.CLASS
                    self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_class_name), token_rehandler=self.handle_token, allow_array=False))

                else:

                    self._vars.state = state.States.RECORD
                    self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_record_name), token_rehandler=self.handle_token, allow_array=False))

            elif token == words.SYNCHRONIZED:

                if self._vars.synchronized: raise exc.SynchronizedDuplicateException(line)
                self._vars.synchronized = True

            elif token == words.VOLATILE:

                if self._vars.volatile: raise exc.VolatileDuplicateException(line)
                self._vars.volatile = True

            elif token == words.TRANSIENT: 
                
                if self._vars.transient: raise exc.TransientDuplicateException(line)
                self._vars.transient = True

            elif token == words.STATIC:

                if self._vars.static: raise exc.StaticDuplicateException(line)
                self._vars.static = True

            elif token == words.ATSIGN: 
                
                self._stack_handler(parsers.annotation.Parser(annotation_handler=self._unstacking(self._store_annotation), token_rehandler=self.handle_token, skip_begin=True))

            elif token == words.ANGLE_OPEN:

                if self._vars.method_generics is not None: raise exc.GenericsDuplicateException(line)
                self._stack_handler(parsers.generics.Parser(gentype_handler=self._unstacking(self._store_method_generics), skip_begin=True))

            else: 
                
                self._vars.state = state.States.ATTR_BEGIN
                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_attribute_type), token_rehandler=self.handle_token))
                self.handle_token(token)

            return
        
        elif self._vars.state is state.States.CLASS_AFTER_NAME:

            if   token in _INHERIT_TYPE_KEYWORDS:

                it = _INHERIT_TYPE_MAP_BY_KEYWORD[token]
                if it in self._vars.class_subc: raise exc.ClassException(line) # repeated extends or implements
                self._vars.state          = state.States.CLASS_SUPERCLASS
                self._vars.class_subc_cur = it
                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_superclass), token_rehandler=self.handle_token, allow_array=False))

            elif token == words.CURLY_OPEN:

                self._flush_class()

            else: raise exc.ClassException(line)
            return

        elif self._vars.state is state.States.CLASS_SUPERCLASS_NAMED:

            if   token == words.COMMA:

                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_superclass), token_rehandler=self.handle_token, allow_array=False))

            elif token == words.CURLY_OPEN:

                self._flush_class()

            elif token in _INHERIT_TYPE_KEYWORDS: 
                
                self._vars.state = state.States.CLASS_AFTER_NAME
                self.handle_token(token)

            else: raise exc.ClassException(line)
            return
        
        elif self._vars.state is state.States.LOOKAHEAD_1:

            if token == words.PARENTH_OPEN:
                
                parent_class = self._class_stack[-1].class_
                if (parent_class              is not None              and \
                    self._vars.attr_type.name ==     parent_class.name): # constructor, since previously we got a word equal to the class' name

                    self._vars.state = state.States.CONSTRUCTOR_SIGNATURE
                    self._stack_handler(parsers.signature.Parser(signature_handler=self._unstacking(self._store_constructor_signature), skip_begin=True))

                else: raise exc.MethodException(line)

            else:

                self._stack_handler(parsers.name.Parser(name_handler=self._unstacking(self._store_attribute_name), token_rehandler=self.handle_token, if_array=self._if_array_after_attr_name))
                self.handle_token(token)

            return
        
        elif self._vars.state is state.States.LOOKAHEAD_2:

            if   token == words.SEMICOLON:

                self._flush_attribute(decl_only=True)
            
            elif token == words.COMMA:

                self._flush_attribute(decl_only=True, continued=True)
                self._vars.state = state.States.ATTR_MULTI_SEP

            elif token == words.EQUALSIGN:

                self._vars.state            = state.States.ATTR_INITIALIZE
                self._vars.attr_value_parts = list()
                self._vars.attr_nest_depth  = 0
                self._vars.attr_scope_depth = 0
            
            elif token == words.PARENTH_OPEN:

                self._vars.state = state.States.METHOD_SIGNATURE
                self._stack_handler(parsers.signature.Parser(signature_handler=self._unstacking(self._store_method_signature)))
                self.handle_token(token) # re-handle token ('('), since it was used only for look-ahead

            else: raise exc.AttributeException(line)
            return
            
        elif self._vars.state is state.States.CONSTRUCTOR_DECLARED:

            if token == words.THROWS:

                if self._vars.throws is not None: raise exc.ThrowsDuplicateException(line)
                self._vars.state  = state.States.CONSTRUCTOR_THROWS
                self._vars.throws = list()
                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_constructor_throws), token_rehandler=self.handle_token, allow_array=False))

            else:

                self._vars.state = state.States.CONSTRUCTOR_BODY
                self._stack_handler(parsers.body.Parser(body_handler=self._unstacking(self._flush_constructor)))
                self.handle_token(token) # re-handle token ('{'), since it was used only for look-ahead
            
            return

        elif self._vars.state is state.States.ATTR_MULTI_SEP:

            if not _WORD_PATTERN.match(token): raise exc.AttributeException(line)
            self._vars.attr_name = token
            self._vars.state = state.States.ATTR_MULTI
            return

        elif self._vars.state is state.States.ATTR_MULTI:

            if   token == words.SEMICOLON:

                self._flush_attribute(decl_only=True)
            
            elif token == words.COMMA:

                self._flush_attribute(decl_only=True, continued=True)
                self._vars.state = state.States.ATTR_MULTI_SEP

            else: raise exc.AttributeException(line)
            return

        elif self._vars.state is state.States.CONSTRUCTOR_THROWS_AFTER:

            if token == words.COMMA:

                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_constructor_throws), token_rehandler=self.handle_token, allow_array=False))

            else:

                self._vars.state = state.States.CONSTRUCTOR_DECLARED
                self.handle_token(token)

            return

        elif self._vars.state is state.States.ATTR_INITIALIZE:

            if self._vars.attr_nest_depth  == 0 and \
               self._vars.attr_scope_depth == 0 and \
               token                   == words.SEMICOLON: 
                
                self._flush_attribute()
                self._vars.attr_nest_depth  = None
                self._vars.attr_scope_depth = None
                return

            else:

                self._vars.attr_value_parts.append(token)
                if   token == words.CURLY_OPEN   : self._vars.attr_scope_depth += 1
                elif token == words.CURLY_CLOSE  : self._vars.attr_scope_depth -= 1
                elif token == words.PARENTH_OPEN : self._vars.attr_nest_depth  += 1
                elif token == words.PARENTH_CLOSE: self._vars.attr_nest_depth  -= 1
                return

        elif self._vars.state is state.States.METHOD_DECLARED:

            if   token == words.SEMICOLON:

                self._flush_method(body=None)
            
            elif token == words.THROWS:

                if self._vars.throws is not None: raise exc.ThrowsDuplicateException(line)
                self._vars.state  = state.States.METHOD_THROWS
                self._vars.throws = list()
                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_method_throws), token_rehandler=self.handle_token, allow_array=False))

            elif token == words.DEFAULT:

                self._vars.state = state.States.METHOD_DEFAULT_VALUE

            elif token == words.CURLY_OPEN:

                self._vars.state = state.States.METHOD_BODY
                self._stack_handler(parsers.body.Parser(body_handler=self._unstacking(self._flush_method)))
                self.handle_token(token) # re-handle token ('{'), since it was used only for look-ahead

            else: raise exc.MethodException(line)
            return
        
        elif self._vars.state is state.States.METHOD_DEFAULT_VALUE:

            self._stack_handler(parsers.expr.raw.Parser(expr_handler=self._unstacking(self._store_method_default_value), token_rehandler=self.handle_token))
            return

        elif self._vars.state is state.States.METHOD_DEFAULT_VALUE_AFTER:

            self._flush_method(None)
            return

        elif self._vars.state is state.States.METHOD_THROWS_AFTER:

            if token == words.COMMA:

                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_method_throws), token_rehandler=self.handle_token, allow_array=False))

            else:

                self._vars.state = state.States.METHOD_DECLARED
                self.handle_token(token)

            return

        elif self._vars.state is state.States.ENUM:

            if   token == words.SEMICOLON:

                self._reset_vars()
                self._class_stack[-1].in_enum = False

            elif token == words.CURLY_CLOSE:

                self._vars.state = state.States.DEFAULT
                self.handle_token(token)

            elif token == words.ATSIGN:

                self._stack_handler(parsers.annotation.Parser(annotation_handler=self._unstacking(self._vars.annotations.append), token_rehandler=self.handle_token, skip_begin=True))

            elif not _WORD_PATTERN.match(token):

                raise exc.EnumValueNameException(line)
            
            else:

                self._vars.enumv_name = token
                self._vars.state      = state.States.ENUM_NAMED

            return

        elif self._vars.state is state.States.ENUM_NAMED:

            if token == words.PARENTH_OPEN:
                
                self._stack_handler(parsers.args.Parser(args_handler=self._unstacking(self._store_enumvalue_args)))
                self.handle_token(token) # re-handle token ('('), since it was used only for look-ahead

            else:

                self._vars.state = state.States.ENUM_AFTER_CALLARGS
                self.handle_token(token) # re-handle token, as it was used only for look-ahead

            return

        elif self._vars.state is state.States.ENUM_AFTER_CALLARGS:
            
            self._flush_enum_value()
            if token == words.CURLY_OPEN:

                self._reset_vars()
                parent_class = self._class_stack[-1].class_
                assert parent_class is not None
                self._vars.class_subc = {model.InheritanceTypes.EXTENDS: [model.Type(name=parent_class.name),],}
                self._flush_class()

            else:

                self.handle_token(token) # re-handle token (either semicolon or comma), as it was used only for look-ahead

            return

        elif self._vars.state is state.States.ENUM_DEFINED:
            
            if  token == words.COMMA:

                self._vars.state = state.States.ENUM

            elif token == words.SEMICOLON:

                self._vars.state = state.States.ENUM
                self.handle_token(token)

            elif token == words.CURLY_CLOSE:

                self._reset_vars()
                self.handle_token(token)

            return

        raise NotImplementedError(f'line = {repr(line)}, state = {repr(self._vars.state.name)}')
        
    @typing.override
    def _default_handle_comment     (self, text:str, block:bool):

        self._NEXT.handle_comment(comment=model.Comment(text=text,multiline=block))

    @typing.override
    def _default_handle_spacing     (self, spacing:str):

        if self._vars.state is state.States.ATTR_INITIALIZE:

            assert self._vars.attr_value_parts is not None
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
