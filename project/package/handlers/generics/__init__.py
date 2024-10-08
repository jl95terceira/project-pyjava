import typing

from .   import exc, state
from ... import handlers, words

class Handler(handlers.PartsHandler):

    def __init__(self, after:typing.Callable[[str],None]):

        self._state          = state.States.BEGIN
        self._line :str|None = None
        self._depth          = 0
        self._parts          = list()
        self._after          = after

    @typing.override
    def handle_line(self, line: str): self._line = line

    @typing.override
    def handle_part(self, part:str):

        line = self._line
        if   self._state is state.States.END:

            raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if part is not words.ANGLE_OPEN: raise exc.BadOpeningException(line)
            self._state = state.States.DEFAULT
            self.handle_part(part)
            return

        elif self._state is state.States.DEFAULT:

            self._depth +=  1 if part == words.ANGLE_OPEN  else \
                           -1 if part == words.ANGLE_CLOSE else \
                            0
            self._parts.append(part)
            if self._depth == 0:

                self._stop()

            return

        raise exc.Exception(f'{self._state.name}, {repr(part)},')

    @typing.override
    def handle_comment(self, text: str): pass #TO-DO save comment somewhere

    @typing.override
    def handle_spacing(self, spacing: str): pass #TO-DO save spacing somewhere

    @typing.override
    def handle_newline(self): pass #TO-DO save newline somewhere

    def _stop(self): 
        
        self._state = state.States.END
        self._after(''.join(self._parts))
