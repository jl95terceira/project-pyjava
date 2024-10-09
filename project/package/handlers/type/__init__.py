import re
import typing

from .            import exc, state
from ...          import handlers, model, util, words
from ...batteries import *

_WORD_PATTERN                = re.compile('^\\w+$')

class Handler(handlers.PartsHandler):

    def __init__(self, after   :typing.Callable[[model.Type],None], 
                 part_rehandler:typing.Callable[[str],None], 
                 can_be_array  :bool=True):

        self._state             = state.States.BEGIN
        self._subhandler:handlers.PartsHandler|None \
                                = None
        self._line :str|None    = None
        self._parts:list[str]   = list()
        self._can_be_array      = can_be_array
        self._array_dim         = 0
        self._type_generics     = ''
        self._after             = after
        self._part_rehandler    = part_rehandler

    def _stack_handler              (self, handler:handlers.PartsHandler): self._subhandler = handler

    def _unstack_handler            (self): self._subhandler = None

    def _unstacking                 (self, f): return ChainedCall(lambda *a, **ka: self._unstack_handler(), f)

    def _store_type_generics        (self, generics:str):

        self._type_generics = generics
        self._stop(part_to_rehandle=None)

    @typing.override
    def handle_line(self, line: str): self._line = line

    @typing.override
    def handle_part   (self, part:str): 
        
        line = self._line
        if self._subhandler is not None:

            self._subhandler.handle_part(part)
            return

        if self._state   is state.States.BEGIN:

            if not _WORD_PATTERN.match(part):

                raise exc.InvalidNameException(line)
            
            self._parts.append(part)
            self._state  = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            if   part in words.ANGLE_OPEN: # generic type - nest

                self._state = state.States.GENERICS
                self._stack_handler(handlers.generics.Handler(after=self._store_type_generics))
                self.handle_part(part)

            elif part == words.SQUARE_OPEN:
                
                if not self._can_be_array: raise exc.ArrayNotAllowedException(line)
                self._state = state.States.ARRAY_OPEN

            elif part == words.DOT:

                self._parts.append(part)
                self._state  = state.States.AFTERDOT

            else:

                self._stop(part)

        elif self._state is state.States.ARRAY_OPEN:

            if part == words.SQUARE_CLOSED:

                self._state = state.States.ARRAY_CLOSE
                self._array_dim += 1

            else: raise exc.ArrayNotClosedException(line)

        elif self._state is state.States.ARRAY_CLOSE:

            if part == words.SQUARE_OPEN:

                self._state = state.States.DEFAULT
                self.handle_part(part)

            else:

                self._stop(part)

        elif self._state is state.States.AFTERDOT:

            if not _WORD_PATTERN.match(part): raise exc.Exception(line)
            self._parts.append(part)
            self._state = state.States.DEFAULT

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def handle_comment(self, text: str): 
        
        line = self._line
        if self._subhandler is not None:

            self._subhandler.handle_comment(text)
            return

        pass #TO-DO

    @typing.override
    def handle_spacing(self, spacing:str): 

        line = self._line
        if self._subhandler is not None:

            self._subhandler.handle_spacing(spacing)
            return

        pass #TO-DO

    @typing.override
    def handle_newline(self): 

        line = self._line
        if self._subhandler is not None:

            self._subhandler.handle_newline()
            return

        pass #TO-DO

    @typing.override
    def handle_eof(self):

        line = self._line
        if self._subhandler is not None:

            self._subhandler.handle_eof()
            return

        if self._state != state.States.DEFAULT: raise exc.EOFExcpetion(line)
        self._stop(None)

    def _stop(self, part_to_rehandle:str|None):

        self._state = state.States.END
        self._after(model.Type(name=''.join(self._parts), generics=self._type_generics, array_dim=self._array_dim))
        if part_to_rehandle is not None:

            self._part_rehandler(part_to_rehandle)
