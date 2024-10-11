import re
import typing

from .            import exc, state
from ...          import handlers, parsers, model, util, words
from ...batteries import *

_WORD_PATTERN = re.compile('^\\w+$')

class Parser(handlers.part.Handler):

    def __init__(self, after:typing.Callable[[dict[str,model.Argument]],None]):

        self._line      :str             |None = None
        self._subhandler:handlers.part.Handler\
                                         |None = None
        self._sign                             = dict()
        self._sign_state                       = state.States.BEGIN
        self._sign_after                       = after
        self._arg_name  :str             |None = None
        self._arg_type  :model.Type      |None = None
        self._arg_annot :model.Annotation|None = None
        self._finality                         = model.FinalityTypes.DEFAULT

    def _stack_handler              (self, handler:handlers.part.Handler): self._subhandler = handler

    def _unstack_handler            (self): self._subhandler = None

    def _unstacking                 (self, f): return ChainedCall(lambda *a, **ka: self._unstack_handler(), f)

    def _store_arg                  (self):

        self._sign[self._arg_name] = model.Argument(type      =self._arg_type, 
                                                    final     =self._finality is model.FinalityTypes.FINAL,
                                                    annotation=self._arg_annot)
        self._arg_name  = None
        self._arg_type  = None
        self._arg_annot = None

    def _store_arg_type             (self, type:model.Type):

        self._arg_type   = type
        self._sign_state = state.States.ARG_TYPED

    def _store_arg_annotation       (self, annot:model.Annotation):

        self._arg_annot  = annot
        self._sign_state = state.States.DEFAULT

    @typing.override
    def handle_line(self, line: str): 
        
        self._line = line
        if self._subhandler is not None:

            self._subhandler.handle_line(line)

    @typing.override
    def handle_part(self, part:str): 
        
        if self._subhandler is not None:

            self._subhandler.handle_part(part)
            return

        line = self._line
        if   self._sign_state is state.States.BEGIN:

            if  part != words.PARENTH_OPEN:

                raise exc.Exception(line)
            
            self._sign_state = state.States.DEFAULT

        elif self._sign_state is state.States.DEFAULT:

            if   part == words.PARENTH_CLOSE:

                if self._finality  is not model.FinalityTypes.DEFAULT or \
                   self._arg_annot is not None                       : raise exc.Exception(line)
                
                self._stop()

            elif part == words.FINAL:

                self._finality = model.FinalityTypes.FINAL

            elif part == words.ATSIGN:

                self._stack_handler(parsers.annotation.Parser(after=self._unstacking(self._store_arg_annotation), part_rehandler=self.handle_part))
                self.handle_part(part)

            else:

                self._stack_handler(parsers.type.Parser(after=self._unstacking(self._store_arg_type), part_rehandler=self.handle_part))
                self.handle_part(part)

        elif self._sign_state is state.States.ARG_TYPED:

            self._arg_name   = part
            self._sign_state = state.States.ARG_NAMED
        
        elif self._sign_state is state.States.ARG_NAMED:

            if   part == words.COMMA:

                self._store_arg()
                self._sign_state = state.States.ARG_SEPARATE
            
            elif part == words.PARENTH_CLOSE:

                self._store_arg ()
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
    def handle_comment(self, text: str): 
        
        if self._subhandler is not None:

            self._subhandler.handle_part(text)
            return

        pass #TO-DO

    @typing.override
    def handle_spacing(self, spacing: str): 
        
        if self._subhandler is not None:

            self._subhandler.handle_spacing(spacing)
            return

        pass #TO-DO

    @typing.override
    def handle_newline(self): 
        
        if self._subhandler is not None:

            self._subhandler.handle_newline()
            return

        pass #TO-DO

    @typing.override
    def handle_eof(self):
        
        line = self._line
        raise exc.EOFException(line) # there should not be an EOF at all, before closing the signature
