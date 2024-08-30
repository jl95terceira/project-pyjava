_DEBUG = 1

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

    def __init__         (self):

        self._stmt_handler                                = L2Handler()
        self._part             :str                       = ''
        self._scope_depth      :int                       = 0
        self._class_name_stack :list[str|None]            = list()
        # resettable state
        # state machine-related
        self._state                                       = state.States.BEGIN
        # etc.
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
        self._method_impl_depth:int                       = 0

    def _reset_state                (self):

        self._state             = state.States.BEGIN
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
        self._arg_name          = None
        self._arg_type_name     = None
        self._args             .clear()
        self._method_impl_depth = 0

    def _coerce_access              (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.PACKAGE_PRIVATE

    def _coerce_finality            (self, finality:model.FinalityType|None):

        return finality if finality is not None else model.FinalityTypes.DEFAULT

    def _flush_import               (self):

        self._stmt_handler.handle_import(name  =self._imported,
                                         static=self._static)
        self._reset_state()

    def _flush_package              (self):

        self._stmt_handler.handle_package(name=self._package)
        self._reset_state()

    def _flush_class                (self):

        self._stmt_handler.handle_class(name      =self._class_name, 
                                        static    =self._static,
                                        access    =self._coerce_access(self._access),
                                        finality  =self._coerce_finality(self._finality),
                                        type      =self._class_type,
                                        extends   =self._class_extends,
                                        implements=self._class_implements)
        self._flush_open(class_name=self._class_name)

    def _flush_open                 (self, class_name:str|None=None):

        self._class_name_stack.append(class_name)
        self._reset_state()
        self._scope_depth += 1

    def _flush_close                (self):

        self._stmt_handler.handle_class_end()
        self._reset_state()
        self._scope_depth -= 1

    def _flush_attr_decl            (self):

        self._stmt_handler.handle_attr(name     =self._attr_name, 
                                       static   =self._static,
                                       final    =self._finality is model.FinalityTypes.FINAL,
                                       access   =self._coerce_access(self._access), 
                                       type_name=self._type_name,
                                       value    =None)
        self._reset_state()

    def _flush_attr_declinit        (self):

        self._stmt_handler.handle_attr(name     =self._attr_name, 
                                       static   =self._static,
                                       final    =self._finality is model.FinalityTypes.FINAL,
                                       access   =self._coerce_access(self._access), 
                                       type_name=self._type_name,
                                       value    =''.join(self._body_parts))
        self._reset_state()

    def _flush_method_decl          (self): 
        
        self._stmt_handler.handle_method(name      =self._attr_name,
                                         static    =self._static,
                                         access    =self._coerce_access(self._access),
                                         finality  =self._coerce_finality(self._finality),
                                         type_name =self._type_name,
                                         args      =self._args,
                                         body      =None)
        self._reset_state()

    def _flush_method_impl          (self): 
        
        self._stmt_handler.handle_method(name      =self._attr_name,
                                         static    =self._static,
                                         access    =self._coerce_access(self._access),
                                         finality  =self._coerce_finality(self._finality),
                                         type_name =self._type_name,
                                         args      =self._args,
                                         body      =''.join(self._body_parts))
        self._reset_state()

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

    def handle_part(self, part:str, line:str): 
        
        def _pad(x:str,v:int): return (lambda s: f'{s}{(v-len(s))*' '}')(x if isinstance(x, str) else str(x))
        if _DEBUG: print(
            _pad(self._state,                        40), 
            _pad("static" if self._static else "",    8), 
            _pad(self._access,                       35), 
            _pad(self._type_name,                    15), 
            repr(part)
        )
        self._part = part
        if   self._state is state.States.BEGIN:

            if   part == words.SEMICOLON  : pass
            elif part == words.BRACE_OPEN : self._flush_open ()
            elif part == words.BRACE_CLOSE: self._flush_close()
            elif part == words.IMPORT     : self._state = state.States.IMPORT
            elif part == words.PACKAGE    : self._state = state.States.PACKAGE
            elif part in FINALITY_TYPE_NAMES_SET: 
                
                if self._finality is not None: raise exc.Exception(line)
                self._finality = FINALITY_TYPE_MAP_BY_NAME[part]

            elif part in ACCESS_MOD_NAMES_SET:

                if self._access is not None: raise exc.Exception(line)
                self._access = ACCESS_MOD_MAP_BY_NAME[part]

            elif part in CLASS_TYPE_NAMES_SET:

                if self._class_type is not None: raise exc.Exception(line)
                self._class_type = CLASS_TYPE_MAP_BY_NAME[part]
                self._state = state.States.CLASS_BEGIN

            elif part == words.STATIC    :

                if self._static: raise exc.Exception(line)
                self._static = True

            elif part == words.ATSIGN    : self._state = state.States.ANNOTATION
            else: 
                
                self._type_name  = part
                self._state      = state.States.TYPED_BEGIN

            return
        
        elif self._state is state.States.PACKAGE:

            if self._package is None: 

                self._package = part
                return
            
            if part == words.SEMICOLON:

                self._flush_package()
                return

            else:

                self._package += part
                return

            raise exc.PackageException(line)
        
        elif self._state is state.States.IMPORT:

            if self._imported is None: 

                if part == words.STATIC: 
                    
                    self._static = True
                    return
                
                self._imported = part
                return

            if part == words.SEMICOLON:

                self._flush_import()
                return

            else:

                self._imported += part
                return

            raise exc.ImportException(line)
        
        elif self._state is state.States.ANNOTATION:

            self._stmt_handler.handle_annotation(part)
            self._reset_state()
            return
        
        elif self._state is state.States.CLASS_BEGIN:

            self._class_name  = part
            self._state = state.States.CLASS_AFTER_NAME
            return

        elif self._state is state.States.CLASS_AFTER_NAME:

            if   part == words.EXTENDS:

                if self._class_extends is not None: raise exc.ClassException(line)
                self._state = state.States.CLASS_EXTENDS
                return

            if part == words.IMPLEMENTS:

                if self._class_implements: raise exc.ClassException(line)
                self._state = state.States.CLASS_IMPLEMENTS
                return

            if part == words.BRACE_OPEN:

                self._flush_class()
                return

            raise exc.ClassException(line)

        elif self._state is state.States.CLASS_EXTENDS:

            self._class_extends = part
            self._state   = state.States.CLASS_AFTER_NAME
            return

        elif self._state is state.States.CLASS_IMPLEMENTS:

            self._store_implements()
            return

        elif self._state is state.States.CLASS_IMPLEMENTS_NAMED:

            if part == words.COMMA:

                self._state = state.States.CLASS_IMPLEMENTS_AFTER
                return

            if part == words.BRACE_OPEN:

                self._flush_class()
                return

            raise exc.ClassImplementsException(line)
        
        elif self._state is state.States.CLASS_IMPLEMENTS_AFTER:

            self._store_implements()
            return

        elif self._state is state.States.TYPED_BEGIN:

            if part in words.ANGLE_OPEN:

                self._type_name += part
                self._generic_depth += 1
                return

            elif part in words.ANGLE_CLOSE:

                self._type_name += part
                self._generic_depth -= 1
                return

            elif self._generic_depth > 0:

                self._type_name += part
                return

            self._attr_name  = part
            self._state = state.States.TYPED_NAMED
            return
        
        elif self._state is state.States.TYPED_NAMED:

            if part == words.SEMICOLON:

                self._flush_attr_decl()
                return
            
            if part == words.EQUALSIGN:

                self._state = state.States.ATTR_INITIALIZE
                return
            
            if part == words.PARENTH_OPEN:

                self._state = state.States.METHOD_SIGNATURE
                return

            else: raise exc.AttributeException(line)
            
        elif self._state is state.States.ATTR_INITIALIZE:

            if part == words.SEMICOLON: 
                
                self._flush_attr_declinit()
                return

            else:

                self._body_parts.append(part)
                return

        elif self._state is state.States.METHOD_SIGNATURE:

            if part == words.PARENTH_CLOSE:

                self._state = state.States.METHOD_DECLARED
                return

            self._store_method_arg_type_name()
            return
        
        elif self._state is state.States.METHOD_ARG_TYPED:

            self._arg_name   = part
            self._state      = state.States.METHOD_ARG_NAMED
            return
        
        elif self._state is state.States.METHOD_ARG_NAMED:

            self._store_method_arg()
            if part == words.COMMA:

                self._state = state.States.METHOD_ARG_AFTER
                return
            
            if part == words.PARENTH_CLOSE:

                self._state = state.States.METHOD_DECLARED
                return

            raise exc.MethodException(line)

        elif self._state is state.States.METHOD_ARG_AFTER:

            self._store_method_arg_type_name()
            return

        elif self._state is state.States.METHOD_DECLARED:

            if part == words.SEMICOLON:

                self._flush_method_decl()
                return
            
            if part == words.BRACE_OPEN:

                self._state              = state.States.METHOD_IMPLEMENTATION
                self._method_impl_depth  = self._scope_depth
                self._scope_depth      += 1
                return

            raise exc.MethodException(line)
        
        elif self._state is state.States.METHOD_IMPLEMENTATION:

            if part == words.BRACE_OPEN:

                self._scope_depth += 1

            elif part == words.BRACE_CLOSE:

                self._scope_depth -= 1
                if self._scope_depth == self._method_impl_depth:

                    self._flush_method_impl()
                    return

            self._body_parts.append(part)
            return

        raise NotImplementedError(line)

    def handle_comment(self, comment:str, line:str):

        print(f'Hello, comment: {repr(comment)}')

    def handle_spacing(self, spacing:str, line:str):

        if self._state is state.States.METHOD_IMPLEMENTATION:

            self._body_parts.append(spacing)
