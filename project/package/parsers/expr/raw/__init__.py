import re
import typing

from .            import exc, state
from ....          import handlers, model, parsers, words

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after         :typing.Callable[[str],None],
                       part_rehandler:typing.Callable[[str],None]):

        super().__init__()
        self._after          = after
        self._part_rehandler = part_rehandler
        self._state          = state.States.DEFAULT
        self._value_parts    = list()
        self._nest_depth     = 0
        self._scope_depth    = 0

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_part(self, part: str):
        
        line = self._line
        if   self._state is state.States.END: raise exc.StopException(line)
        elif self._state is state.States.DEFAULT:

            if self._nest_depth  == 0 and \
               self._scope_depth == 0 and \
               (part == words.SEMICOLON     or \
                part == words.COMMA         or \
                part == words.PARENTH_CLOSE): 
                
                self._stop(part)
                return

            else:

                self._value_parts.append(part)
                if   part == words.CURLY_OPEN   : self._scope_depth += 1
                elif part == words.CURLY_CLOSE  : self._scope_depth -= 1
                elif part == words.PARENTH_OPEN : self._nest_depth  += 1
                elif part == words.PARENTH_CLOSE: self._nest_depth  -= 1
                return
        
        else: raise AssertionError(self._state)

    @typing.override
    def _default_handle_spacing(self, spacing: str): pass #TO-DO

    @typing.override
    def _default_handle_newline(self): pass #TO-DO

    @typing.override
    def _default_handle_comment(self, text: str): pass #TO-DO

    @typing.override
    def _default_handle_eof(self): raise NotImplementedError() #TO-DO

    def _stop(self, part_to_rehandle:str|None): 
        
        self._state = state.States.END
        self._after(''.join(self._value_parts))
        if part_to_rehandle is not None:

            self._part_rehandler(part_to_rehandle)
