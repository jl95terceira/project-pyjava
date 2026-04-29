from jl95.batteries import typing

from .   import exc, state
from ..util import *
from ... import words

class Parser(StackingSemiParser):

    def __init__(self, body_handler:typing.Consumer[str],
                       skip_begin=False):

        super().__init__()
        self._state         = state.States.BEGIN   if not skip_begin else \
                              state.States.DEFAULT
        self._depth         = 0 if not skip_begin else \
                              1
        self._parts         = list()
        self._handler       = body_handler

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_token(self, token:str):

        line = self._line
        if   self._state is state.States.END:

            raise exc.StopException(line)

        elif self._state is state.States.BEGIN:

            if self._depth != 0:

                raise AssertionError(f'{self._depth=}')

            if token != words.CURLY_OPEN:

                raise exc.InvalidOpenException(line)
           
            else:
               
                self._state = state.States.DEFAULT
                self._depth += 1

        elif self._state is state.States.DEFAULT:

            if token == words.CURLY_OPEN:

                self._depth += 1
                self._parts.append(token)

            elif token == words.CURLY_CLOSE:

                self._depth -= 1
                if self._depth == 0:

                    self._stop()
                
                else:
                    
                    self._parts.append(token)

            else:

                self._parts.append(token)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment(self, text: str, block: bool):
        
        self._parts.append(((lambda t: f'//{t}') if not block else (lambda t: f'/*{t}*/'))(text))

    @typing.override
    def _default_handle_spacing(self, spacing:str):

        self._parts.append(spacing)

    @typing.override
    def _default_handle_newline(self):

        self.handle_spacing(spacing='\n')

    @typing.override
    def _default_handle_eof(self):
        
        raise exc.EOFException(self._line) # there should not be an EOF at all, before closing the body

    def _stop(self):

        self._state = state.States.END
        self._handler(''.join(self._parts))
