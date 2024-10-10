import typing

from .            import exc, state
from ...          import handlers, parsers, model, words
from ...batteries import *

class Parser(handlers.part.PartsHandler):

    def __init__(self, after         :typing.Callable[[model.Annotation],None],
                       part_rehandler:typing.Callable[[str],None]):

        self._part_rehandler       = part_rehandler
        self._state                = state.States.BEGIN
        self._subhandler:handlers.part.PartsHandler|None \
                                   = None
        self._line :str      |None = None
        self._name :str      |None = ''
        self._args :list[str]|None = list()
        self._after                = after

    def _stack_handler              (self, handler:handlers.part.PartsHandler): 
        
        self._subhandler = handler
        self._subhandler.handle_line(self._line)

    def _unstack_handler            (self): self._subhandler = None

    def _unstacking                 (self, f): return ChainedCall(lambda *a, **ka: self._unstack_handler(), f)

    def _store_args                 (self, args:list[str]): 
        
        self._args = args
        self._stop(None)

    @typing.override
    def handle_line(self, line: str): 
        
        if self._subhandler is not None:

            self._subhandler.handle_line(line)
            return

        self._line = line

    @typing.override
    def handle_part   (self, part:str):
        
        if self._subhandler is not None:

            self._subhandler.handle_part(part)
            return

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
    def handle_comment(self, text: str):
        
        if self._subhandler is not None:

            self._subhandler.handle_comment(text)
            return

    @typing.override
    def handle_spacing(self, spacing:str):

        if self._subhandler is not None:

            self._subhandler.handle_spacing(spacing)
            return

    @typing.override
    def handle_newline(self):

        if self._subhandler is not None:

            self._subhandler.handle_newline(self)
            return

    @typing.override
    def handle_eof    (self):

        line = self._line
        if self._state != state.States.NAMED: raise exc.Exception(line)
        self._stop(None)

    def _stop(self, part_to_rehandle:str|None):

        self._state = state.States.END
        self._after(model.Annotation(name=self._name,
                                     args=self._args))
        if part_to_rehandle is not None: self._part_rehandler(part_to_rehandle)
