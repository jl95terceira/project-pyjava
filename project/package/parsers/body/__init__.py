import typing

from .   import exc, state
from ... import handlers, parsers, words

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after     :typing.Callable[[str],None],
                       skip_begin=False):

        super().__init__()
        self._state         = state.States.BEGIN   if not skip_begin else \
                              state.States.DEFAULT
        self._depth         = 0                    if not skip_begin else \
                              1
        self._parts         = list()
        self._after         = after

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_part   (self, part:str):

        line = self._line
        if   self._state is state.States.END:

            raise exc.StopException(line)

        elif self._state is state.States.BEGIN:

            if self._depth != 0:

                raise AssertionError(f'{self._depth=}')

            if part != words.CURLY_OPEN:

                raise exc.InvalidOpenException(line)
           
            else:
               
                self._state = state.States.DEFAULT
                self._depth += 1

        elif self._state is state.States.DEFAULT:

            if part == words.CURLY_OPEN:

                self._depth += 1
                self._parts.append(part)

            elif part == words.CURLY_CLOSE:

                self._depth -= 1
                if self._depth == 0:

                    self._stop()
                
                else:
                    
                    self._parts.append(part)

            else:

                self._parts.append(part)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment(self, text: str):
        
        self._parts.append(text)

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
        self._after(''.join(self._parts))
