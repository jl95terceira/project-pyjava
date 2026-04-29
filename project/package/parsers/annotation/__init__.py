from ..util import *

from jl95.batteries import typing

from .   import exc, state
from ... import parsers, model, words

class Parser(StackingSemiParser):

    def __init__(self, annotation_handler:typing.Consumer[model.Annotation],
                       token_rehandler    :typing.Consumer[str],
                       skip_begin=False):

        super().__init__()
        self._token_rehandler      = token_rehandler
        self._state                = state.States.BEGIN   if not skip_begin else \
                                     state.States.DEFAULT
        self._name :str      |None = ''
        self._args :list[str]|None = list()
        self._handler              = annotation_handler

    def _store_name                 (self, name:str):

        self._name  = name
        self._state = state.States.NAMED

    def _store_args                 (self, args:list[str]): 
        
        self._args = args
        self._stop(None)

    @typing.override
    def _default_handle_line   (self, line: str): pass

    @typing.override
    def _default_handle_token  (self, token:str):
        
        line = self._line
        if   self._state is state.States.BEGIN:

            if token != words.ATSIGN: raise exc.Exception(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            self._stack_handler(parsers.name.Parser(name_handler=self._unstacking(self._store_name), token_rehandler=self.handle_token))
            self.handle_token(token)

        elif self._state is state.States.NAMED:

            if token != words.PARENTH_OPEN: 
                
                self._stop(token)

            else:

                self._stack_handler(parsers.args.Parser(args_handler=self._unstacking(self._store_args)))
                self.handle_token(token)
            
        elif self._state is state.States.END:

            raise exc.StopException(line)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment(self, text: str, block:bool): pass

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
        assert self._name is not None
        assert self._args is not None
        self._handler(model.Annotation(name=self._name,
                                     args=self._args))
        if part_to_rehandle is not None: self._token_rehandler(part_to_rehandle)
