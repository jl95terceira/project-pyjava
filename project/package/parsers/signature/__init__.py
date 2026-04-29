import re
from jl95.batteries import typing

from .       import exc, state
from ..util import *
from ...     import parsers, model, words

class Parser(StackingSemiParser):

    def __init__(self, signature_handler:typing.Consumer[dict[str,model.Argument]],
                       skip_begin=False):

        super().__init__()
        self._sign                                   = dict()
        self._state                                  = state.States.BEGIN   if not skip_begin else \
                                                       state.States.DEFAULT
        self._handler                                = signature_handler
        self._arg_name       :str             |None  = None
        self._arg_type       :model.Type      |None  = None
        self._arg_annotations:list[model.Annotation] = list()
        self._arg_varargs                            = False
        self._finality                               = model.FinalityTypes.DEFAULT

    def _store_arg                  (self):

        assert self._arg_type is not None
        self._sign[self._arg_name] = model.Argument(type       =self._arg_type, 
                                                    final      =self._finality is model.FinalityTypes.FINAL,
                                                    annotations=self._arg_annotations,
                                                    varargs    =self._arg_varargs)
        self._arg_name        = None
        self._arg_type        = None
        self._arg_annotations = list()
        self._arg_varargs     = False
        self._finality        = model.FinalityTypes.DEFAULT

    def _store_arg_type             (self, type:model.Type):

        self._arg_type   = type
        self._state = state.States.ARG_TYPED

    def _store_arg_name             (self, name:str):

        self._arg_name   = name
        self._state = state.States.ARG_NAMED

    def _if_array_after_name        (self, dim:int):

        assert self._arg_type is not None
        self._arg_type.array_dim += dim

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_token(self, token:str): 
        
        line = self._line
        if   self._state is state.States.BEGIN:

            if  token != words.PARENTH_OPEN: raise exc.Exception(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            if   token == words.PARENTH_CLOSE:

                if self._finality is not model.FinalityTypes.DEFAULT or \
                   self._arg_annotations                            : raise exc.Exception(line)
                
                self._stop()

            elif token == words.FINAL:

                self._finality = model.FinalityTypes.FINAL

            elif token == words.ATSIGN:

                self._stack_handler(parsers.annotation.Parser(annotation_handler=self._unstacking(self._arg_annotations.append), token_rehandler=self.handle_token))
                self.handle_token(token)

            else:

                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_arg_type), token_rehandler=self.handle_token))
                self.handle_token(token)

        elif self._state is state.States.ARG_TYPED:

            if token == words.ELLIPSIS:

                if self._arg_varargs: raise exc.Exception(line)
                self._arg_varargs = True

            else:

                self._stack_handler(parsers.name.Parser(name_handler=self._unstacking(self._store_arg_name), token_rehandler=self.handle_token, if_array=self._if_array_after_name))
                self.handle_token(token)
        
        elif self._state is state.States.ARG_NAMED:

            if   token == words.COMMA:

                self._store_arg()
                self._state = state.States.ARG_SEPARATE
            
            elif token == words.PARENTH_CLOSE:

                self._store_arg()
                self._stop()

            else: raise exc.Exception(line)

        elif self._state is state.States.ARG_SEPARATE:

            self._state = state.States.DEFAULT
            self.handle_token(token)

        else: raise AssertionError(f'{self._state=}')

    def _stop(self):

        self._state = state.States.END
        self._handler(self._sign)

    @typing.override
    def _default_handle_comment(self, text: str, block:bool): pass #TO-DO

    @typing.override
    def _default_handle_spacing(self, spacing: str): pass #TO-DO

    @typing.override
    def _default_handle_newline(self): pass #TO-DO

    @typing.override
    def _default_handle_eof(self):
        
        raise exc.EOFException(self._line) # there should not be an EOF at all, before closing the signature
