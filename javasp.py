import dataclasses
import re
import typing

import batteries             as batteries
from   javasp_state import *
from   javasp_exc   import *
from   javasp_model import *

PATTERN_WORD_BEGIN = '^|(?<!\\w)'
PATTERN_WORD_END   = '$|(?!\\w)'
PATTERN_WORD       = '(?:[\\w\\.:])+'
PATTERN            = re.compile(f'((?:{PATTERN_WORD_BEGIN})(?:{PATTERN_WORD})(?:{PATTERN_WORD_END})|[^\\s])|(\\s+)')

class L2Handler: 

    def handle_package    (name:str): 
        
        print(f'Handling package: {name}')

    def handle_import     (name:str,static:bool): 
        
        print(f'Handling{' static' if static else ''} import: {name}')
        
    def handle_annotation (name:str): 
        
        print(f'Handling annotation: {name}')

    def handle_class      (name:str, extends:str|None, implements:list[str]): 
        
        print(f'Handling class: {name}')

    def handle_block_begin(): 

        print(f'Handling block begin ({repr('{')})')

    def handle_block_end  (): 

        print(f'Handling block end ({repr('}')})')

JAVA_ACCESS_MOD_NAMES_SET   = {am.name    for am in AccessModifiers.values()}
JAVA_ACCESS_MOD_MAP_BY_NAME = {am.name:am for am in AccessModifiers.values()}

class L1Handler:

    def __init__         (self):

        self._stmt_handler = L2Handler()
        self._state        = L1States.NONE
        # resettable state
        self._package      :str               |None = None
        self._static       :bool                    = False
        self._imported     :str               |None = None
        self._access_mod   :AccessModifier|None = None
        self._class_name   :str               |None = None
        self._implements   :list[str]               = list()

    def _set_state       (self, state:L1State):

        self._state = state

    def _reset_state     (self):

        self._set_state(L1States.NONE)
        self._package    = None
        self._static     = False
        self._imported   = None
        self._access_mod = None
        self._class_name = None
        self._implements.clear()

    def _accuse_undefined(self, part:str): raise NotImplementedError(f'no handling defined at state {repr(self._state)} for part {repr(part)}')

    def handle_part(self, part:str, line:str): 
        
        print(part)
        return
        if part == ';':

            if   self._state is L1States.NONE   : pass
            if   self._state is L1States.PACKAGE: 

                self._stmt_handler.handle_package(self._package)

            elif self._state is L1States.IMPORT : 
                
                self._stmt_handler.handle_import(self._imported, static=True)
            
            self._reset_state()
            return

        elif self._state is L1States.NONE:

            if   part == 'import' : self._set_state(L1States.IMPORT)
            elif part == 'package': self._set_state(L1States.PACKAGE)
            elif part == 'class'  : self._set_state(L1States.CLASS)
            elif part == '@'      : self._set_state(L1States.ANNOTATION)
            elif part in JAVA_ACCESS_MOD_NAMES_SET:

                self._access_mod = JAVA_ACCESS_MOD_MAP_BY_NAME[part]

            else: self._accuse_undefined(part)
        
        elif self._state is L1States.PACKAGE:

            if self._package is None: 

                self._package = part

            else: raise JavaParserPackageException(line)
        
        elif self._state is L1States.IMPORT:

            if   part == 'static': 
                
                self._static = True

            else:

                if not self._imported: 

                    self._imported = part

                elif part == '*':

                    self._imported += part

                else: raise JavaParserImportException(line)
        
        elif self._state is L1States.ANNOTATION:

            self._stmt_handler.handle_annotation(part)
            self._reset_state()
        
        elif self._state is L1States.CLASS:

            self._class_name = part
            self._set_state(L1States.CLASS_NAMED)

        elif self._state is L1States.CLASS_NAMED:

            if   part == 'extends':

                self._set_state(L1States.CLASS_EXTENDS)

            elif part == 'implements':

                self._set_state(L1States.CLASS_IMPLEMENTS)

            elif part == '{':

                self._reset_state()

            else: raise JavaParserClassException(line)

        else: raise NotImplementedError(f'No handling defined while in state {self._state} for {repr(part)}')

class L0Handler:

    def __init__(self):

        self._next_handler = L1Handler()

    def handle_line(self, line:str):

        string_parts = []
        for match in re.finditer(pattern=PATTERN, string=line):

            g = match.group(1)
            if g is None: continue
            if g.startswith("\""):

                if re.match(string=g, pattern='()"$'): pass
                elif string_parts: raise Exception()

            self._next_handler.handle_part(part=g, line=line)

def parse(source:str):

    jph = L0Handler()
    for line in source.splitlines():

        jph.handle_line(line)
