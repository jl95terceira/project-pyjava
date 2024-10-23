import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words

_WORD_PATTERN = re.compile('^(?:\\w|\\$)+$')

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after         :typing.Callable[[str],None],
                       part_rehandler:typing.Callable[[str],None],
                       allow_wildcard=False,
                       if_array      :typing.Callable[[int],None]|None=None):

        super().__init__()
        self._after                = after
        self._part_rehandler       = part_rehandler
        self._allow_wildcard       = allow_wildcard
        self._if_array             = if_array
        self._state                = state.States.BEGIN
        self._array_dim            = 0
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

            if   part == words.DOT:

                self._state = state.States.AFTER_DOT

            elif part == words.SQUARE_OPEN and self._if_array is not None:

                self._state = state.States.ARRAY_OPEN

            else:

                self._stop()
                self._part_rehandler(part)

        elif self._state is state.States.AFTER_DOT:

            if part == words.ASTERISK:

                if not self._allow_wildcard: raise exc.WildcardNotAllowedException(line)
                self._parts.append('*')
                self._stop()

            else:

                if not _WORD_PATTERN.match(part): raise exc.Exception(line)
                self._parts.append(part)
                self._state = state.States.DEFAULT

        elif self._state is state.States.ARRAY_OPEN:

            if part != words.SQUARE_CLOSED: raise exc.Exception(line)
            self._state = state.States.ARRAY_CLOSE
            self._array_dim += 1

        elif self._state is state.States.ARRAY_CLOSE:

            if self._part == words.SQUARE_OPEN:

                self._state = state.States.DEFAULT
                self.handle_part(part)

            else: 
                
                self._stop()
                self._part_rehandler(part)

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
        if self._if_array is not None:

            self._if_array(self._array_dim)
