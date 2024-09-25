import re
import typing

from .    import exc, state
from ...  import sub
from .... import handlers, model, util, words
from ....batteries import *

_WORD_PATTERN = re.compile('^\\w+$')

class Handler(handlers.PartsHandler):

    def __init__(self, after:typing.Callable[[list[str]],None]):

        self._line          :str      |None = None
        self._callargs      :list[str]      = list()
        self._callargs_state                = state.CallArgsStates.BEGIN
        self._callarg_value                 = ''
        self._callarg_depth                 = 0
        self._callargs_after                = after

    def _store_callarg(self):

        self._callargs.append(self._callarg_value)
        self._callarg_value = ''
        self._callarg_depth = 0

    @typing.override
    def handle_line(self, line: str): self._line = line

    @typing.override
    def handle_part(self, part:str):

        line = self._line
        if self._callargs_state is state.CallArgsStates.BEGIN:

            if part != words.PARENTH_OPEN:

                raise exc.Exception(line)
            
            else:

                self._callargs_state  = state.CallArgsStates.DEFAULT
                self._callarg_value  = ''
                self._callarg_depth += 1

        elif self._callargs_state is state.CallArgsStates.DEFAULT:

            if part == words.PARENTH_CLOSE:

                self._callarg_depth -= 1
                if self._callarg_depth != 0:

                    self._callarg_value += part

                else:

                    self._after_callargs()

            elif part == words.PARENTH_OPEN:

                self._callarg_depth += 1
                self._callarg_value += part

            elif part == words.COMMA:

                if self._callarg_depth == 0:

                    self._store_callarg()
                    self._callargs_state = state.CallArgsStates.SEPARATE
                
                else:

                    self._callarg_value += part

            else:

                self._callarg_value += part

        elif self._callargs_state is state.CallArgsStates.SEPARATE: 
            
            if part == words.PARENTH_CLOSE: 
                
                raise exc.Exception(line)
            
            self._callargs_state = state.CallArgsStates.DEFAULT
            self.handle_part(part) # re-handle part, since it was used only for look-ahead

        else: raise AssertionError(f'{self._callargs_state=}')

    @typing.override
    def handle_comment(self, text: str): pass #TO-DO

    @typing.override
    def handle_spacing(self, spacing: str): pass #TO-DO

    @typing.override
    def handle_newline(self): pass #TO-DO

    def _after_callargs             (self):

        if self._callarg_value:

            self._store_callarg()

        self._state = state.CallArgsStates.END
        self._callargs_after(self._callargs)
