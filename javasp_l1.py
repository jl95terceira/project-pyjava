DEBUG = 0

import javasp_l1_state as state
import javasp_l1_exc   as exc
import javasp_model    as model
import javasp_words    as words
from javasp_l2 import L2Handler

ACCESS_MOD_NAMES_SET   = {am.name    for am in model.AccessModifiers.values()}
ACCESS_MOD_MAP_BY_NAME = {am.name:am for am in model.AccessModifiers.values()}

class L1Handler:

    def __init__         (self):

        self._stmt_handler                              = L2Handler()
        self._part           :str                       = ''
        self._scope_depth    :int                       = 0
        # resettable state
        # state machine-related
        self.state                                      = state.States.BEGIN
        # etc.
        self.package         :str                 |None = None
        self.static          :bool                      = False
        self.imported        :str                 |None = None
        self.access          :model.AccessModifier|None = None
        self.class_name      :str                 |None = None
        self.class_extends   :str                 |None = None
        self.class_implements:list[str]                 = list()
        self.type_name       :str                 |None = None
        self.attr_name       :str                 |None = None
        self.expr_parts      :list[str]                 = list()
        self.arg_name        :str                 |None = None
        self.arg_type_name   :str                 |None = None
        self.args            :list[model.Argument]      = list()

    def reset_state         (self):

        self.state            = state.States.BEGIN
        self.package          = None
        self.static           = False
        self.imported         = None
        self.access           = None
        self.class_name       = None
        self.class_extends    = None
        self.class_implements.clear()
        self.type_name        = None
        self.attr_name        = None
        self.expr_parts      .clear()
        self.arg_name         = None
        self.arg_type_name    = None
        self.args            .clear()

    def assert_unreserved   (self): 

        if words.is_reserved(self._part): raise exc.ReservedWordException(f'reserved word {repr(self._part)} not allowed while in state {repr(self.state)}')

    def coerce_access       (self, access:model.AccessModifier|None):

        return access if access is not None else model.AccessModifiers.PACKAGE_PRIVATE

    def flush_import        (self):

        self._stmt_handler.handle_import(name  =self.imported,
                                         static=self.static)
        self.reset_state()

    def flush_package       (self):

        self._stmt_handler.handle_package(name=self.package)
        self.reset_state()

    def flush_class         (self):

        self._stmt_handler.handle_class(name      =self.class_name, 
                                        static    =self.static,
                                        access    =self.coerce_access(self.access),
                                        extends   =self.class_extends,
                                        implements=self.class_implements)
        self.reset_state()

    def flush_class_and_open(self):

        self.flush_class()
        self.flush_open ()

    def flush_open          (self):

        self._stmt_handler.handle_scope_begin()
        self.reset_state()
        self._scope_depth += 1

    def flush_close         (self):

        self._stmt_handler.handle_scope_end()
        self.reset_state()
        self._scope_depth -= 1

    def flush_attr_decl     (self):

        self._stmt_handler.handle_attr_decl(name     =self.attr_name, 
                                            static   =self.static,
                                            access   =self.coerce_access(self.access), 
                                            type_name=self.type_name)
        self.reset_state()

    def flush_attr_declinit (self):

        self._stmt_handler.handle_attr_declinit(name     =self.attr_name, 
                                                static   =self.static,
                                                access   =self.coerce_access(self.access), 
                                                type_name=self.type_name,
                                                value    =''.join(self.expr_parts))
        self.reset_state()

    def flush_method_decl   (self): 
        
        self._stmt_handler.handle_method_decl(name      =self.attr_name,
                                              static    =self.static,
                                              access    =self.coerce_access(self.access),
                                              type_name =self.type_name,
                                              args      =self.args)
        self.reset_state()

    def flush_method_impl   (self): pass

    def store_implements           (self):

        self.assert_unreserved()
        self.class_implements.append(self._part)
        self.state = state.States.CLASS_IMPLEMENTS_NAMED

    def store_method_arg_type_name (self):

        self.assert_unreserved()
        self.arg_type_name = self._part
        self.state         = state.States.METHOD_ARG_TYPED

    def store_method_arg           (self):

        self.args.append(model.Argument(name=self.arg_name, type_name=self.arg_type_name))
        self.arg_name       = None
        self.arg_type_name  = None

    def handle_part         (self, part:str, line:str): 
        
        def _pad(x:str,v:int): return (lambda s: f'{s}{(v-len(s))*' '}')(x if isinstance(x, str) else str(x))
        if DEBUG: print(_pad(self.state,                        40), 
                       _pad("static" if self.static else "",    8), 
                       _pad(self.access,                       35), 
                       _pad(self.type_name,                    15), part)
        self._part = part
        if   self.state is state.States.BEGIN:

            if   part == words.SEMICOLON  : pass
            elif part == words.BRACE_OPEN : self.flush_open ()
            elif part == words.BRACE_CLOSE: self.flush_close()
            elif part == words.IMPORT     : self.state = state.States.IMPORT
            elif part == words.PACKAGE    : self.state = state.States.PACKAGE
            elif part in ACCESS_MOD_NAMES_SET:

                if self.access is not None: raise exc.Exception(line)
                self.access = ACCESS_MOD_MAP_BY_NAME[part]

            elif part == words.STATIC    :

                if self.static: raise exc.Exception(line)
                self.static = True

            elif part == words.CLASS     : 
                
                self.state = state.States.CLASS_BEGIN

            elif part == words.ATSIGN    : self.state = state.States.ANNOTATION
            else: 
                
                self.type_name  = part
                self.state      = state.States.TYPED_BEGIN

            return
        
        elif self.state is state.States.PACKAGE:

            if self.package is None: 

                self.assert_unreserved()
                self.package = part
                return
            
            if part == words.SEMICOLON:

                self.flush_package()
                return

            raise exc.PackageException(line)
        
        elif self.state is state.States.IMPORT:

            if not self.imported: 

                if part == words.STATIC: 
                    
                    self.static = True
                    return
                
                self.assert_unreserved()
                self.imported = part
                return

            if part == words.SEMICOLON:

                self.flush_import()
                return

            raise exc.ImportException(line)
        
        elif self.state is state.States.ANNOTATION:

            self.assert_unreserved()
            self._stmt_handler.handle_annotation(part)
            self.reset_state()
            return
        
        elif self.state is state.States.CLASS_BEGIN:

            self.assert_unreserved()
            self.class_name  = part
            self.state = state.States.CLASS_AFTER_NAME
            return

        elif self.state is state.States.CLASS_AFTER_NAME:

            if   part == words.EXTENDS:

                if self.class_extends is not None: raise exc.ClassException(line)
                self.state = state.States.CLASS_EXTENDS
                return

            if part == words.IMPLEMENTS:

                if self.class_implements: raise exc.ClassException(line)
                self.state = state.States.CLASS_IMPLEMENTS
                return

            if part == words.BRACE_OPEN:

                self.flush_class_and_open()
                return

            raise exc.ClassException(line)

        elif self.state is state.States.CLASS_EXTENDS:

            self.assert_unreserved()
            self.class_extends = part
            self.state   = state.States.CLASS_AFTER_NAME
            return

        elif self.state is state.States.CLASS_IMPLEMENTS:

            self.store_implements()
            return

        elif self.state is state.States.CLASS_IMPLEMENTS_NAMED:

            if part == words.COMMA:

                self.state = state.States.CLASS_IMPLEMENTS_AFTER
                return

            if part == words.BRACE_OPEN:

                self.flush_class_and_open()
                return

            raise exc.ClassImplementsException(line)
        
        elif self.state is state.States.CLASS_IMPLEMENTS_AFTER:

            self.store_implements()
            return

        elif self.state is state.States.TYPED_BEGIN:

            self.assert_unreserved()
            self.attr_name  = part
            self.state = state.States.TYPED_NAMED
            return
        
        elif self.state is state.States.TYPED_NAMED:

            if part == words.SEMICOLON:

                self.flush_attr_decl()
                return
            
            if part == words.EQUALSIGN:

                self.state = state.States.ATTR_INITIALIZE
                return
            
            if part == words.PARENTH_OPEN:

                self.state = state.States.METHOD_SIGNATURE
                return

            else: raise exc.AttributeException(line)
            
        elif self.state is state.States.ATTR_INITIALIZE:

            if part == words.SEMICOLON: 
                
                self.flush_attr_declinit()
                return

            else:

                self.expr_parts.append(part)
                return

        elif self.state is state.States.METHOD_SIGNATURE:

            self.store_method_arg_type_name()
            return
        
        elif self.state is state.States.METHOD_ARG_TYPED:

            self.assert_unreserved()
            self.arg_name   = part
            self.state      = state.States.METHOD_ARG_NAMED
            return
        
        elif self.state is state.States.METHOD_ARG_NAMED:

            self.store_method_arg()
            if part == words.COMMA:

                self.state = state.States.METHOD_ARG_AFTER
                return
            
            if part == words.PARENTH_CLOSE:

                self.store_method_arg()
                self.state = state.States.METHOD_DECLARED
                return

            raise exc.MethodException(line)

        elif self.state is state.States.METHOD_ARG_AFTER:

            self.store_method_arg_type_name()
            return

        elif self.state is state.States.METHOD_DECLARED:

            if part == words.SEMICOLON:

                self.flush_method_decl()
                return
            
            raise exc.MethodException(line)

        raise NotImplementedError(line)

