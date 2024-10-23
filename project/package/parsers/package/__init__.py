import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after     :typing.Callable[[model.Package],None],
                       skip_begin=False):

        super().__init__()
        self._after          = after
        self._state          = state.States.BEGIN         if not skip_begin else \
                               state.States.AFTER_PACKAGE
        self._name :str|None = None

    def _store_name(self, name:str):

        self._name = name
        self._state = state.States.AFTER_NAME

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_part     (self, part:str): 
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if part != words.PACKAGE: raise exc.Exception(line)
            self._state = state.States.AFTER_PACKAGE

        elif self._state is state.States.AFTER_PACKAGE:

            self._stack_handler(parsers.name.Parser(after=self._unstacking(self._store_name), part_rehandler=self.handle_part))
            self.handle_part(part)

        elif self._state is state.States.AFTER_NAME:

            if part != words.SEMICOLON: raise exc.Exception(line)
            self._stop()

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment  (self, text: str): pass #TO-DO

    @typing.override
    def _default_handle_spacing  (self, spacing:str): pass #TO-DO

    @typing.override
    def _default_handle_newline  (self): pass #TO-DO

    @typing.override
    def _default_handle_eof      (self): raise exc.EOFException(self._line) # there should not be a EOF at all, before semi-colon

    def _stop(self): 
        
        self._state = state.States.END
        self._after(model.Package(name=self._name))
