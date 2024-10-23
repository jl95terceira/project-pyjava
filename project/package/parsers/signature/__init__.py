import re
import typing

from .            import exc, state
from ...          import parsers, model, words

class Parser(parsers.entity.StackingSemiParser):

    def __init__(self, after     :typing.Callable[[dict[str,model.Argument]],None],
                       skip_begin=False):

        super().__init__()
        self._sign                                   = dict()
        self._sign_state                             = state.States.BEGIN   if not skip_begin else \
                                                       state.States.DEFAULT
        self._sign_after                             = after
        self._arg_name       :str             |None  = None
        self._arg_type       :model.Type      |None  = None
        self._arg_annotations:list[model.Annotation] = list()
        self._arg_varargs                            = False
        self._finality                               = model.FinalityTypes.DEFAULT

    def _store_arg                  (self):

        self._sign[self._arg_name] = model.Argument(type       =self._arg_type, 
                                                    final      =self._finality is model.FinalityTypes.FINAL,
                                                    annotations=self._arg_annotations,
                                                    varargs    =self._arg_varargs)
        self._arg_name        = None
        self._arg_type        = None
        self._arg_annotations = list()
        self._arg_varargs     = False
        self._finality        = model.FinalityTypes.DEFAULT

    def _store_arg_type             (self, type:model.Type):

        self._arg_type   = type
        self._sign_state = state.States.ARG_TYPED

    def _store_arg_name             (self, name:str):

        self._arg_name   = name
        self._sign_state = state.States.ARG_NAMED

    def _if_array_after_name        (self, dim:int):

        self._arg_type.array_dim += dim

    @typing.override
    def _default_handle_line(self, line: str): pass

    @typing.override
    def _default_handle_part(self, part:str): 
        
        line = self._line
        if   self._sign_state is state.States.BEGIN:

            if  part != words.PARENTH_OPEN: raise exc.Exception(line)
            self._sign_state = state.States.DEFAULT

        elif self._sign_state is state.States.DEFAULT:

            if   part == words.PARENTH_CLOSE:

                if self._finality is not model.FinalityTypes.DEFAULT or \
                   self._arg_annotations                            : raise exc.Exception(line)
                
                self._stop()

            elif part == words.FINAL:

                self._finality = model.FinalityTypes.FINAL

            elif part == words.ATSIGN:

                self._stack_handler(parsers.annotation.Parser(after=self._unstacking(self._arg_annotations.append), part_rehandler=self.handle_part))
                self.handle_part(part)

            else:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_arg_type), part_rehandler=self.handle_part))
                self.handle_part(part)

        elif self._sign_state is state.States.ARG_TYPED:

            if part == words.ELLIPSIS:

                if self._arg_varargs: raise exc.Exception(line)
                self._arg_varargs = True

            else:

                self._stack_handler(parsers.name.Parser(after=self._unstacking(self._store_arg_name), part_rehandler=self.handle_part, if_array=self._if_array_after_name))
                self.handle_part(part)
        
        elif self._sign_state is state.States.ARG_NAMED:

            if   part == words.COMMA:

                self._store_arg()
                self._sign_state = state.States.ARG_SEPARATE
            
            elif part == words.PARENTH_CLOSE:

                self._store_arg()
                self._stop()

            else: raise exc.Exception(line)

        elif self._sign_state is state.States.ARG_SEPARATE:

            self._sign_state = state.States.DEFAULT
            self.handle_part(part)

        else: raise AssertionError(f'{self._sign_state=}')

    def _stop(self):

        self._state = state.States.END
        self._sign_after(self._sign)

    @typing.override
    def _default_handle_comment(self, text: str): pass #TO-DO

    @typing.override
    def _default_handle_spacing(self, spacing: str): pass #TO-DO

    @typing.override
    def _default_handle_newline(self): pass #TO-DO

    @typing.override
    def _default_handle_eof(self):
        
        raise exc.EOFException(self._line) # there should not be an EOF at all, before closing the signature
