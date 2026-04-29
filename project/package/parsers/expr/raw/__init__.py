import re
from jl95.batteries import typing

from .        import exc, state
from ...util import *
from ....     import words

class Parser(StackingSemiParser):

    def __init__(self, expr_handler   :typing.Consumer[str],
                       token_rehandler:typing.Consumer[str]):

        super().__init__()
        self._handler         = expr_handler
        self._token_rehandler = token_rehandler
        self._state           = state.States.DEFAULT
        self._value_parts     = list()
        self._nest_depth      = 0
        self._scope_depth     = 0

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_token(self, token: str):
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException(line)
        elif self._state is state.States.DEFAULT:

            if self._nest_depth  == 0 and \
               self._scope_depth == 0 and \
               (token == words.SEMICOLON     or \
                token == words.COMMA         or \
                token == words.PARENTH_CLOSE): 
                
                self._stop(token)
                return

            else:

                self._value_parts.append(token)
                if   token == words.CURLY_OPEN   : self._scope_depth += 1
                elif token == words.CURLY_CLOSE  : self._scope_depth -= 1
                elif token == words.PARENTH_OPEN : self._nest_depth  += 1
                elif token == words.PARENTH_CLOSE: self._nest_depth  -= 1
                return
        
        else: raise AssertionError(self._state)

    @typing.override
    def _default_handle_spacing(self, spacing: str): pass #TO-DO

    @typing.override
    def _default_handle_newline(self): pass #TO-DO

    @typing.override
    def _default_handle_comment(self, text: str, block:bool): pass #TO-DO

    @typing.override
    def _default_handle_eof(self): raise NotImplementedError() #TO-DO

    def _stop(self, part_to_rehandle:str|None): 
        
        self._state = state.States.END
        self._handler(''.join(self._value_parts))
        if part_to_rehandle is not None:

            self._token_rehandler(part_to_rehandle)
