import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words
from ...batteries import *

_WORD_PATTERN                = re.compile('^\\w+$')

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after   :typing.Callable[[model.Package],None]):

        super().__init__()
        self._after            = after
        self._state            = state.States.BEGIN
        self._package:str|None = None

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_part     (self, part:str): 
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if part != words.PACKAGE: raise exc.Exception(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            self._package = part
            self._state = state.States.DEFAULT_2

        elif self._state is state.States.DEFAULT_2:

            if part == words.SEMICOLON:

                self._stop()

            elif part == words.DOT          or \
                 part == words.ASTERISK     or \
                 not words.is_reserved(part):

                self._package += part

            else: raise exc.Exception(line)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment  (self, text: str): pass #TO-DO

    @typing.override
    def _default_handle_spacing  (self, spacing:str): pass #TO-DO

    @typing.override
    def _default_handle_newline  (self): pass #TO-DO

    @typing.override
    def _default_handle_eof      (self): raise exc.EOFException(self._line) # there should not be a EOF at all, before semi-colon

    def _stop(self): 
        
        self._state = state.States.END
        self._after(model.Package(name=self._package))
