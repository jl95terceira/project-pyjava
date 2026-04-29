import re
from jl95.batteries import typing

from .       import exc, state
from ..util import *
from ...     import model, parsers, words

_CONSTRAINT_TYPE_MAP_BY_KEYWORD = {words.EXTENDS: model.TypeConstraints.EXTENDS,
                                   words.SUPER  : model.TypeConstraints.SUPER}
_CONSTRAINT_TYPE_KEYWORDS       = set(_CONSTRAINT_TYPE_MAP_BY_KEYWORD)
_WORD_PATTERN                   = re.compile('^\\w+$')

class Parser(StackingSemiParser):

    def __init__(self, gentype_handler:typing.Consumer[list[model.GenericType]],
                       skip_begin=False):

        super().__init__()
        self._state                                         = state.States.BEGIN   if not skip_begin else \
                                                              state.States.DEFAULT
        self._depth                                         = 0
        self._parts_backlog:list[str]                       = list()
        self._constrained_type_name\
                           :str                       |None = None
        self._targets      :list[model.Type]                = list()
        self._types        :list[model.GenericType]         = list()
        self._constraint   :model.TypeConstraint      |None = None
        self._handler                                       = gentype_handler

    def _store_type                 (self, type:model.GenericType): 

        self._types.append(type)
        self._state = state.States.AFTER

    def _store_constrained_type     (self):

        self._types.append(model.ConstrainedType(name      =self._constrained_type_name,
                                                 targets   =self._types,
                                                 constraint=self._constraint if self._constraint is not None else model.TypeConstraints.NONE))
        self._state = state.States.AFTER

    def _store_target_type          (self, type:model.Type):

        self._types.append(type)
        self._state = state.States.CONSTRAINT_LOOKAHEAD

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_token(self, token:str):

        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if token != words.ANGLE_OPEN: raise exc.BadOpeningException(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            self._parts_backlog.clear()
            if   token == words.ANGLE_CLOSE:

                self._stop()

            else:

                self._parts_backlog.append(token)
                self._state = state.States.DEFAULT_2
            
        elif self._state is state.States.DEFAULT_2:

            self._parts_backlog.append(token)
            if token not in _CONSTRAINT_TYPE_KEYWORDS:

                part0 = self._parts_backlog[0]
                if part0 == words.QUESTIONMARK:

                    self._store_type(model.UnboundedType())

                else:

                    self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_type), token_rehandler=self.handle_token, allow_array=True, allow_annotations=True))
                    self.handle_token(part0)

                self.handle_token(token)

            else:

                self._constrained_type_name = self._parts_backlog[0]
                self._state = state.States.CONSTRAINT
                self.handle_token(token)
            
        elif self._state is state.States.CONSTRAINT:

            self._constraint = _CONSTRAINT_TYPE_MAP_BY_KEYWORD[token]
            self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_target_type), token_rehandler=self.handle_token, allow_array=False))

        elif self._state is state.States.CONSTRAINT_LOOKAHEAD:

            if token != words.AMPERSAND:

                self._store_constrained_type()
                self.handle_token(token)

            else:

                self._stack_handler(parsers.type.Parser(type_handler=self._unstacking(self._store_target_type), token_rehandler=self.handle_token, allow_array=False))

        elif self._state is state.States.AFTER:

            if token == words.ANGLE_CLOSE: 
                
                self._stop()

            elif token == words.COMMA: 
                
                self._state = state.States.SEP

            else: raise exc.Exception(line)

        elif self._state is state.States.SEP:

            self._state = state.States.DEFAULT
            self.handle_token(token)

        else: raise NotImplementedError(f'{self._state.name}, {repr(token)},')

    @typing.override
    def _default_handle_comment(self, text: str, block:bool): pass #TO-DO save comment somewhere

    @typing.override
    def _default_handle_spacing(self, spacing: str): pass #TO-DO save spacing somewhere

    @typing.override
    def _default_handle_newline(self): pass #TO-DO save newline somewhere

    @typing.override
    def _default_handle_eof(self):
        
        raise exc.EOFException(self._line) # there should not be an EOF at all, before closing the comprehension

    def _stop(self): 
        
        self._state = state.States.END
        self._handler(self._types)
