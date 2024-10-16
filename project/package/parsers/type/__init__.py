import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words
from ...batteries import *

_WORD_PATTERN = re.compile('^\\w+$')

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after   :typing.Callable[[model.Type],None], 
                 part_rehandler:typing.Callable[[str],None], 
                 can_be_array  =True):

        super().__init__()
        self._state                                     = state.States.BEGIN
        self._parts       :list[str]                    = list()
        self._can_be_array                              = can_be_array
        self._array_dim                                 = 0
        self._generics    :list[model.GenericType]|None = None
        self._after                                     = after
        self._part_rehandler                            = part_rehandler
        # ...
        self._stack_handler(parsers.name.Parser(after=self._unstacking(self._store_name), part_rehandler=self.handle_part))

    def _store_name     (self, name:str):

        self._parts.append(name)
        self._state = state.States.AFTER_NAME

    def _store_generics (self, generics:list[model.GenericType]):

        self._generics = generics
        self._stop(part_to_rehandle=None)

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_part     (self, part:str): 
        
        line = self._line
        if self._state   is state.States.BEGIN:
            
            raise AssertionError()

        elif self._state is state.States.AFTER_NAME:

            if   part in words.ANGLE_OPEN: # generic type - nest

                self._state = state.States.GENERICS
                self._stack_handler(parsers.generics.Parser(after=self._store_generics))
                self.handle_part(part)

            elif part == words.SQUARE_OPEN:
                
                if not self._can_be_array: raise exc.ArrayNotAllowedException(line)
                self._state = state.States.ARRAY_OPEN

            else:

                self._stop(part)

        elif self._state is state.States.ARRAY_OPEN:

            if part == words.SQUARE_CLOSED:

                self._state = state.States.ARRAY_CLOSE
                self._array_dim += 1

            else: raise exc.ArrayNotClosedException(line)

        elif self._state is state.States.ARRAY_CLOSE:

            if part == words.SQUARE_OPEN:

                self._state = state.States.AFTER_NAME
                self.handle_part(part)

            else:

                self._stop(part)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment  (self, text: str): pass #TO-DO

    @typing.override
    def _default_handle_spacing  (self, spacing:str): pass #TO-DO

    @typing.override
    def _default_handle_newline  (self): pass #TO-DO

    @typing.override
    def _default_handle_eof      (self):

        if self._state != state.States.AFTER_NAME: raise exc.EOFException(self._line)
        self._stop(None)

    def _stop(self, part_to_rehandle:str|None): 

        self._state = state.States.END
        self._after(model.Type(name     =''.join(self._parts), 
                               generics =self._generics, 
                               array_dim=self._array_dim))
        if part_to_rehandle is not None:

            self._part_rehandler(part_to_rehandle)
