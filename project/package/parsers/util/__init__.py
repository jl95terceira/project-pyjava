import abc
from jl95.batteries import typing

from ... import handlers
from .. import DEBUG

from jl95.batteries import joincallables

class StackingSemiParser(handlers.token.Handler, abc.ABC):

    def __init__(self):

        self._subhandler:handlers.token.Handler|None = None
        self._line      :str                   |None = None
        self._part      :str                   |None = None

    def _stack_handler              (self, handler:handlers.token.Handler):

        self._subhandler = handler
        assert self._line is not None
        self._subhandler.handle_line(self._line)

    def _unstack_handler            (self):

        self._subhandler = None

    def _unstacking                 (self, f): return joincallables(lambda *a, **ka: self._unstack_handler(), f)

    @typing.override
    def handle_line                 (self, line:str):

        self._line = line
        if self._subhandler is not None: self._subhandler.handle_line(line)
        else                           : self.   _default_handle_line(line)

    @typing.override
    def handle_token                 (self, token:str): 
        
        if DEBUG: print(f'{self.__class__.__module__}.{type(self).__name__}  :: {repr(token)}')
        self._part = token
        if self._subhandler is not None: self._subhandler.handle_token(token)
        else                           : self.   _default_handle_token(token)

    @typing.override
    def handle_comment              (self, text:str, block:bool):

        if self._subhandler is not None: self._subhandler.handle_comment(text,block)
        else                           : self.   _default_handle_comment(text,block)

    @typing.override
    def handle_spacing              (self, spacing:str):

        if self._subhandler is not None: self._subhandler.handle_spacing(spacing)
        else                           : self.   _default_handle_spacing(spacing)

    @typing.override
    def handle_newline              (self):

        if self._subhandler is not None: self._subhandler.handle_newline()
        else                           : self.   _default_handle_newline()

    @typing.override
    def handle_eof                  (self):
        
        if self._subhandler is not None: self._subhandler.handle_eof()
        self._default_handle_eof()

    @abc.abstractmethod
    def _default_handle_line        (self, line:str): ...

    @abc.abstractmethod
    def _default_handle_token       (self, token:str): ...

    @abc.abstractmethod
    def _default_handle_comment     (self, text:str, block:bool): ...

    @abc.abstractmethod
    def _default_handle_spacing     (self, spacing:str): ...

    @abc.abstractmethod
    def _default_handle_newline     (self): ...

    @abc.abstractmethod
    def _default_handle_eof         (self): ...

