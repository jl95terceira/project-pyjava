from jl95.batteries import typing

from .       import exc, state
from ..util import *
from ...     import handlers, words

class Parser(StackingSemiParser):

    def __init__(self, import_handler:typing.Consumer[handlers.decl.ImportDeclaration],
                       skip_begin=False):

        super().__init__()
        self._handler         = import_handler
        self._state           = state.States.BEGIN        if not skip_begin else \
                                state.States.AFTER_IMPORT
        self._static          = False
        self._name  :str|None = None

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_token     (self, token:str): 
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if token != words.IMPORT: raise exc.Exception(line)
            self._state = state.States.AFTER_IMPORT

        elif self._state is state.States.AFTER_IMPORT:

            if token == words.STATIC: 
                
                self._static = True

            else:
                            
                self._name = token
                self._state    = state.States.AFTER_NAME 

        elif self._state is state.States.AFTER_NAME:

            if token == words.SEMICOLON:

                self._stop()
                return

            elif token == words.DOT          or \
                 token == words.ASTERISK     or \
                 not words.is_reserved(token):

                self._name += token

            else: raise exc.Exception(line)

        elif self._state is state.States.AFTER_NAME:

            if token == words.SEMICOLON:

                self._stop()

            elif token == words.DOT          or \
                 token == words.ASTERISK     or \
                 not words.is_reserved(token):

                self._import += token

            else: raise exc.Exception(line)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment  (self, text: str, block:bool): pass #TO-DO

    @typing.override
    def _default_handle_spacing  (self, spacing:str): pass #TO-DO

    @typing.override
    def _default_handle_newline  (self): pass #TO-DO

    @typing.override
    def _default_handle_eof      (self): raise exc.EOFException(self._line) # there should not be a EOF at all, before semi-colon

    def _stop(self): 
        
        self._state = state.States.END
        self._handler(handlers.decl.ImportDeclaration(name  =self._name,
                                                      static=self._static))
