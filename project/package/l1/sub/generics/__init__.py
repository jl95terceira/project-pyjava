import typing

from .    import state
from .    import exc
from .... import words

class Handler:

    def __init__(self, after:typing.Callable[[str],None]):

        self._state = state.States.BEGIN
        self._depth = 0
        self._parts = list()
        self._after = after
        self._part:str|None = None
        self._line:str|None = None

    def __call__(self, part:str, line:str):

        self._part = part
        self._line = line
        self._handler()

    def _handler(self):

        if   self._state is state.States.END:

            raise exc.StopException()

        if   self._state is state.States.BEGIN:

            if self._part is not words.ANGLE_OPEN: raise exc.BadOpeningException(self._line)
            self._state = state.States.DEFAULT
            self._handler()
            return

        elif self._state is state.States.DEFAULT:

            self._depth +=  1 if self._part == words.ANGLE_OPEN  else \
                           -1 if self._part == words.ANGLE_CLOSE else \
                            0
            self._parts.append(self._part)
            if self._depth == 0:

                self._stop()

            return

        raise exc.Exception(f'{self._state.name}, {repr(self._part)},')

    def _stop(self): 
        
        self._state = state.States.END
        self._after(''.join(self._parts))
