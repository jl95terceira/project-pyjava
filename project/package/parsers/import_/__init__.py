import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words
from ...batteries import *

_WORD_PATTERN                = re.compile('^\\w+$')

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after   :typing.Callable[[model.Import],None]):

        super().__init__()
        self._after             = after
        self._state             = state.States.BEGIN
        self._static            = False
        self._imported:str|None = None

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_part     (self, part:str): 
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if part != words.IMPORT: raise exc.Exception(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            if part == words.STATIC: 
                
                self._static = True

            else:
                            
                self._imported = part
                self._state    = state.States.DEFAULT_2 

        elif self._state is state.States.DEFAULT_2:

            if part == words.SEMICOLON:

                self._stop()
                return

            elif part == words.DOT          or \
                 part == words.ASTERISK     or \
                 not words.is_reserved(part):

                self._imported += part

            else: raise exc.Exception(line)

        elif self._state is state.States.DEFAULT_2:

            if part == words.SEMICOLON:

                self._stop()

            elif part == words.DOT          or \
                 part == words.ASTERISK     or \
                 not words.is_reserved(part):

                self._import += part

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
        self._after(model.Import(name  =self._imported,
                                 static=self._static))
