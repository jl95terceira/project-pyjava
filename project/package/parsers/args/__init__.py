import re
from jl95.batteries import typing

from .            import exc, state
from ...          import handlers, parsers, words

_ACREMENTERS  = {words.PARENTH_OPEN: words.PARENTH_CLOSE,
                 words.CURLY_OPEN  : words.CURLY_CLOSE,
                 words.ANGLE_OPEN  : words.ANGLE_CLOSE}

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after:typing.Consumer[list[str]]):

        super().__init__()
        self._args                 :list[str] = list()
        self._args_state                      = state.CallArgsStates.BEGIN
        self._arg_value                       = ''
        self._arg_depth                       = 0
        self._arg_depth_incrementer:str|None  = None
        self._args_after                      = after

    def _store_arg(self):

        self._args.append(self._arg_value)
        self._arg_value = ''
        self._arg_depth = 0

    @typing.override
    def _default_handle_line   (self, line: str): pass

    @typing.override
    def _default_handle_part   (self, part:str):
        
        line = self._line
        if   self._args_state is state.CallArgsStates.BEGIN:

            if part != words.PARENTH_OPEN:

                raise exc.InvalidOpenException(line)
            
            else:

                self._args_state  = state.CallArgsStates.DEFAULT
                self._arg_value  = ''

        elif self._args_state is state.CallArgsStates.DEFAULT:

            if self._arg_depth_incrementer is not None:

                if   part == self._arg_depth_incrementer:

                    self._arg_depth += 1

                elif part == _ACREMENTERS[self._arg_depth_incrementer]:

                    self._arg_depth -= 1
                    if self._arg_depth == 0:

                        self._arg_depth_incrementer = None

                self._arg_value += part

            elif part == words.PARENTH_CLOSE:

                self._stop()

            elif part in _ACREMENTERS:

                self._arg_depth_incrementer = part
                self.handle_part(part)

            elif part == words.COMMA:

                self._store_arg()
                self._args_state = state.CallArgsStates.SEPARATE

            else:

                self._arg_value += part

        elif self._args_state is state.CallArgsStates.SEPARATE: 
            
            if part == words.PARENTH_CLOSE: 
                
                raise exc.AfterSeparatorException(line)
            
            self._args_state = state.CallArgsStates.DEFAULT
            self.handle_part(part) # re-handle part, since it was used only for look-ahead

        else: raise AssertionError(f'{self._args_state=}')

    @typing.override
    def _default_handle_comment(self, text: str, block:bool): pass #TO-DO

    @typing.override
    def _default_handle_spacing(self, spacing: str): self._arg_value += spacing

    @typing.override
    def _default_handle_newline(self): pass #TO-DO

    @typing.override
    def _default_handle_eof(self):
        
        line = self._line
        raise exc.EOFException(line) # there should not be an EOF at all, before closing the arguments comprehension

    def _stop(self):

        if self._arg_value:

            self._store_arg()

        self._state = state.CallArgsStates.END
        self._args_after(self._args)
