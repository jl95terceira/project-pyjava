import typing

from .            import exc, state
from ...          import handlers, parsers, model, words
from ...batteries import *

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after         :typing.Callable[[model.Annotation],None],
                       part_rehandler:typing.Callable[[str],None]):

        super().__init__()
        self._part_rehandler       = part_rehandler
        self._state                = state.States.BEGIN
        self._line :str      |None = None
        self._name :str      |None = ''
        self._args :list[str]|None = list()
        self._after                = after

    def _store_args                 (self, args:list[str]): 
        
        self._args = args
        self._stop(None)

    @typing.override
    def _default_handle_line   (self, line: str): pass

    @typing.override
    def _default_handle_part   (self, part:str):
        
        line = self._line
        if   self._state is state.States.BEGIN:

            if part != words.ATSIGN: raise exc.Exception(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            if words.is_reserved(part): raise exc.Exception(line)
            self._name  = part
            self._state = state.States.NAMED

        elif self._state is state.States.NAMED:

            if part != words.PARENTH_OPEN: 
                
                self._stop(part)

            else:

                self._stack_handler(parsers.callargs.Parser(after=self._unstacking(self._store_args)))
                self.handle_part(part)
            
        elif self._state is state.States.END:

            raise exc.StopException(line)  

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment(self, text: str): pass

    @typing.override
    def _default_handle_spacing(self, spacing:str): pass

    @typing.override
    def _default_handle_newline(self): pass
    
    @typing.override
    def _default_handle_eof    (self):

        line = self._line
        if self._state != state.States.NAMED: raise exc.Exception(line)
        self._stop(None)

    def _stop(self, part_to_rehandle:str|None):

        self._state = state.States.END
        self._after(model.Annotation(name=self._name,
                                     args=self._args))
        if part_to_rehandle is not None: self._part_rehandler(part_to_rehandle)
