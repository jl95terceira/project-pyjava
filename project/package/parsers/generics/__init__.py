import re
import typing

from .            import exc, state
from ...          import handlers, model, parsers, words
from ...batteries import *

_WORD_PATTERN = re.compile('^\\w+$')

class Parser(handlers.part.PartsHandler):

    def __init__(self, after:typing.Callable[[list[model.Type]],None]):

        self._state                       = state.States.BEGIN
        self._subhandler:handlers.part.PartsHandler\
                            |None         = None
        self._line      :str|None         = None
        self._depth                       = 0
        self._types     :list[model.Type] = list()
        self._after                       = after

    def _stack_handler              (self, handler:handlers.part.PartsHandler):

        self._subhandler = handler
        self._subhandler.handle_line(self._line)

    def _unstack_handler            (self):

        self._subhandler = None

    def _unstacking                 (self, f): return ChainedCall(lambda *a, **ka: self._unstack_handler(), f)

    def _store_type                 (self, type:model.Type): 

        self._types.append(type)
        self._state = state.States.AFTER

    @typing.override
    def handle_line(self, line: str): 
        
        self._line = line
        if self._subhandler is not None:

            self._subhandler.handle_line(line)

    @typing.override
    def handle_part(self, part:str):

        if self._subhandler is not None:

            self._subhandler.handle_part(part)
            return

        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if part != words.ANGLE_OPEN: raise exc.BadOpeningException(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            if part == words.ANGLE_CLOSE:

                self._stop()

            else:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_type), part_rehandler=self.handle_part, can_be_array=True))
                self.handle_part(part)
            
        elif self._state is state.States.AFTER:

            if part == words.ANGLE_CLOSE: 
                
                self._stop()

            elif part == words.COMMA: 
                
                self._state = state.States.SEP

            else: raise exc.Exception(line)

        elif self._state is state.States.SEP:

            if not _WORD_PATTERN.match(part): raise exc.Exception(line)
            self._state = state.States.DEFAULT
            self.handle_part(part)

        else: raise exc.Exception(f'{self._state.name}, {repr(part)},')

    @typing.override
    def handle_comment(self, text: str): pass #TO-DO save comment somewhere

    @typing.override
    def handle_spacing(self, spacing: str): pass #TO-DO save spacing somewhere

    @typing.override
    def handle_newline(self): pass #TO-DO save newline somewhere

    @typing.override
    def handle_eof(self):
        
        if self._subhandler is not None:

            self._subhandler.handle_eof()
            return

        line = self._line
        raise exc.EOFException(line) # there should not be an EOF at all, before closing the comprehension

    def _stop(self): 
        
        self._state = state.States.END
        self._after(self._types)
