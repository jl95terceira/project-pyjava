import re
import typing

from .            import exc, state
from ...          import handlers, model, parsers, words

_CONSTRAINT_TYPE_MAP_BY_KEYWORD = {words.EXTENDS: model.TypeConstraints.EXTENDS,
                                   words.SUPER  : model.TypeConstraints.SUPER}
_CONSTRAINT_TYPE_KEYWORDS       = set(_CONSTRAINT_TYPE_MAP_BY_KEYWORD)
_WORD_PATTERN = re.compile('^\\w+$')

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after     :typing.Callable[[list[model.GenericType]],None],
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
        self._after                                         = after

    def _store_type                 (self, type:model.Type): 

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
    def _default_handle_part(self, part:str):

        line = self._line
        if   self._state is state.States.END: raise exc.StopException()

        elif self._state is state.States.BEGIN:

            if part != words.ANGLE_OPEN: raise exc.BadOpeningException(line)
            self._state = state.States.DEFAULT

        elif self._state is state.States.DEFAULT:

            self._parts_backlog.clear()
            if   part == words.ANGLE_CLOSE:

                self._stop()

            else:

                self._parts_backlog.append(part)
                self._state = state.States.DEFAULT_2
            
        elif self._state is state.States.DEFAULT_2:

            self._parts_backlog.append(part)
            if part not in _CONSTRAINT_TYPE_KEYWORDS:

                part0 = self._parts_backlog[0]
                if part0 == words.QUESTIONMARK:

                    self._store_type(model.UnboundedType())

                else:

                    self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_type), part_rehandler=self.handle_part, allow_array=True, allow_annotations=True))
                    self.handle_part(part0)

                self.handle_part(part)

            else:

                self._constrained_type_name = self._parts_backlog[0]
                self._state = state.States.CONSTRAINT
                self.handle_part(part)
            
        elif self._state is state.States.CONSTRAINT:

            self._constraint = _CONSTRAINT_TYPE_MAP_BY_KEYWORD[part]
            self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_target_type), part_rehandler=self.handle_part, allow_array=False))

        elif self._state is state.States.CONSTRAINT_LOOKAHEAD:

            if part != words.AMPERSAND:

                self._store_constrained_type()
                self.handle_part(part)

            else:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_target_type), part_rehandler=self.handle_part, allow_array=False))

        elif self._state is state.States.AFTER:

            if part == words.ANGLE_CLOSE: 
                
                self._stop()

            elif part == words.COMMA: 
                
                self._state = state.States.SEP

            else: raise exc.Exception(line)

        elif self._state is state.States.SEP:

            self._state = state.States.DEFAULT
            self.handle_part(part)

        else: raise NotImplementedError(f'{self._state.name}, {repr(part)},')

    @typing.override
    def _default_handle_comment(self, text: str): pass #TO-DO save comment somewhere

    @typing.override
    def _default_handle_spacing(self, spacing: str): pass #TO-DO save spacing somewhere

    @typing.override
    def _default_handle_newline(self): pass #TO-DO save newline somewhere

    @typing.override
    def _default_handle_eof(self):
        
        raise exc.EOFException(self._line) # there should not be an EOF at all, before closing the comprehension

    def _stop(self): 
        
        self._state = state.States.END
        self._after(self._types)
