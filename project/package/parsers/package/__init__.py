import re
from jl95.batteries import typing

from .       import exc, state
from ..util import *
from ...     import handlers, parsers, words

class Parser(StackingSemiParser):

    def __init__(self, package_handler:typing.Consumer[handlers.decl.PackageDeclaration],
                       skip_begin=False):

        super().__init__()
        self._handler        = package_handler
        self._state          = state.States.BEGIN         if not skip_begin else \
                               state.States.AFTER_PACKAGE
        self._name :str|None = None

    def _store_name(self, name:str):

        self._name = name
        self._state = state.States.AFTER_NAME

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_token     (self, token:str): 
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if token != words.PACKAGE: raise exc.Exception(line)
            self._state = state.States.AFTER_PACKAGE

        elif self._state is state.States.AFTER_PACKAGE:

            self._stack_handler(parsers.name.Parser(name_handler=self._unstacking(self._store_name), token_rehandler=self.handle_token))
            self.handle_token(token)

        elif self._state is state.States.AFTER_NAME:

            if token != words.SEMICOLON: raise exc.Exception(line)
            self._stop()

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
        
        assert self._name is not None
        self._state = state.States.END
        self._handler(handlers.decl.PackageDeclaration(name=self._name))
