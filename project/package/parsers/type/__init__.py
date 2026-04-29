import re
from jl95.batteries import typing

from .       import exc, state
from ..util import *
from ...     import parsers, model, words

class Parser(StackingSemiParser):

    def __init__(self, type_handler   :typing.Consumer[model.Type], 
                       token_rehandler:typing.Consumer[str], 
                       allow_array      =True,
                       allow_annotations=False):

        super().__init__()
        self._handler                                   = type_handler
        self._token_rehandler                           = token_rehandler
        self._can_be_array                              = allow_array
        self._can_be_annotated                          = allow_annotations
        self._state                                     = state.States.BEGIN
        self._name        :str                    |None = None
        self._array_dim                                 = 0
        self._generics    :list[model.GenericType]|None = None
        self._annotations :list[model.Annotation]       = list()

    def _store_name      (self, name:str):

        self._name  = name
        self._state = state.States.AFTER_NAME

    def _store_generics  (self, generics:list[model.GenericType]):

        self._generics = generics

    @typing.override
    def _default_handle_line     (self, line: str): pass

    @typing.override
    def _default_handle_token     (self, token:str): 
        
        line = self._line
        if self._state   is state.States.BEGIN:
            
            if token != words.ATSIGN:

                self._stack_handler(parsers.name.Parser(name_handler=self._unstacking(self._store_name), token_rehandler=self.handle_token))

            else:

                if not self._can_be_annotated: raise exc.AnnotationsNotAllowedException(line)
                self._stack_handler(parsers.annotation.Parser(annotation_handler=self._unstacking(self._annotations.append), token_rehandler=self.handle_token))

            self.handle_token(token)

        elif self._state is state.States.AFTER_NAME:

            if   token == words.ANGLE_OPEN: # generic type - nest

                if self._generics is not None: raise exc.GenericsDuplicateException(line)
                self._stack_handler(parsers.generics.Parser(gentype_handler=self._unstacking(self._store_generics), skip_begin=True))

            elif token == words.SQUARE_OPEN:
                
                if not self._can_be_array: raise exc.ArrayNotAllowedException(line)
                self._state = state.States.ARRAY_OPEN

            else:

                self._stop(token)

        elif self._state is state.States.ARRAY_OPEN:

            if token == words.SQUARE_CLOSED:

                self._state = state.States.ARRAY_CLOSE
                self._array_dim += 1

            else: raise exc.ArrayNotClosedException(line)

        elif self._state is state.States.ARRAY_CLOSE:

            if token == words.SQUARE_OPEN:

                self._state = state.States.AFTER_NAME
                self.handle_token(token)

            else:

                self._stop(token)

        else: raise AssertionError(f'{self._state=}')

    @typing.override
    def _default_handle_comment  (self, text: str, block:bool): pass #TO-DO

    @typing.override
    def _default_handle_spacing  (self, spacing:str): pass #TO-DO

    @typing.override
    def _default_handle_newline  (self): pass #TO-DO

    @typing.override
    def _default_handle_eof      (self):

        if self._state != state.States.AFTER_NAME: raise exc.EOFException(self._line)
        self._stop(None)

    def _stop(self, part_to_rehandle:str|None): 

        self._state = state.States.END
        assert self._name is not None
        self._handler(model.Type(name       =self._name, 
                               generics   =self._generics, 
                               array_dim  =self._array_dim,
                               annotations=self._annotations))
        if part_to_rehandle is not None:

            self._token_rehandler(part_to_rehandle)
