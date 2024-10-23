import typing

from .            import exc, state
from ...          import handlers, parsers, model, words

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after         :typing.Callable[[model.Annotation],None],
                       part_rehandler:typing.Callable[[str],None],
                       skip_begin    =False):

        super().__init__()
        self._part_rehandler       = part_rehandler
        self._state                = state.States.BEGIN   if not skip_begin else \
                                     state.States.DEFAULT
        self._name :str      |None = ''
        self._args :list[str]|None = list()
        self._after                = after

    def _store_name                 (self, name:str):

        self._name  = name
        self._state = state.States.NAMED

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

            self._stack_handler(parsers.name.Parser(after=self._unstacking(self._store_name), part_rehandler=self.handle_part))
            self.handle_part(part)

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

        if self._state != state.States.NAMED: raise exc.Exception(self._line)
        self._stop(None)

    def _stop(self, part_to_rehandle:str|None):

        self._state = state.States.END
        self._after(model.Annotation(name=self._name,
                                     args=self._args))
        if part_to_rehandle is not None: self._part_rehandler(part_to_rehandle)
