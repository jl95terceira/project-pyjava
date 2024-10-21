import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words
from ...batteries import *

_WORD_PATTERN = re.compile('^(?:\\w|\\$)+$')

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after         :typing.Callable[[str],None],
                       part_rehandler:typing.Callable[[str],None],
                       allow_wildcard=False):

        super().__init__()
        self._after                = after
        self._part_rehandler       = part_rehandler
        self._allow_wildcard       = allow_wildcard
        self._state                = state.States.BEGIN
        self._parts:list[str]|None = None

    @typing.override
    def _default_handle_line     (self, line:str): pass

    @typing.override
    def _default_handle_part     (self, part:str): 
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if not _WORD_PATTERN.match(part): raise exc.Exception(line)
            self._parts = [part,]
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            if part == words.DOT:

                self._state = state.States.AFTER_DOT

            else:

                self._stop()
                self._part_rehandler(part)

        elif self._state is state.States.AFTER_DOT:

            if part == words.ASTERISK:

                if not self._allow_wildcard: raise exc.WildcaldNotAllowedException(line)
                self._parts.append('*')
                self._stop()

            else:

                if not _WORD_PATTERN.match(part): raise exc.Exception(line)
                self._parts.append(part)
                self._state = state.States.DEFAULT

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment  (self, text:str): pass #TO-DO

    @typing.override
    def _default_handle_spacing  (self, spacing:str): pass #TO-DO

    @typing.override
    def _default_handle_newline  (self): pass #TO-DO

    @typing.override
    def _default_handle_eof      (self): 
        
        if self._state is not state.States.DEFAULT: raise exc.EOFException(self._line)
        self._stop()

    def _stop(self): 
        
        self._state = state.States.END
        self._after('.'.join(self._parts)) # if parts has only 1 element, no dot appears - so, no problem
