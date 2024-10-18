import re
import typing

from .   import exc, state
from ... import handlers, parsers

PATTERN  = re.compile(f'((?:(?:\\w|\\$)+)|(?:/\\*)|(?:\\*/)|(?://)|(?:\\\\.)|(?:\\.{{3}})|(?:<{{2,}})|\\s+|.)')

class Parser(handlers.line.Handler):

    def __init__(self, stream_handler:handlers.entity.Handler):

        self._next_handler                 = parsers.entity.Parser(stream_handler=stream_handler)
        self._state                        = state.States.DEFAULT
        self._line         :str      |None = None
        self._comment_parts:list[str]|None = None
        self._string_delim :str      |None = None
        self._string_parts :list[str]|None = None
        self._first_line                   = True

    @typing.override
    def handle_line(self, line:str):
        
        self._next_handler.handle_line(line)
        if   self._state is state.States.IN_COMMENT_ONELINE: # // ...

            self._next_handler.handle_comment(text=''.join(self._comment_parts))
            self._comment_parts = None
            self._state = state.States.DEFAULT # no longer in comment, since this is another line

        elif self._state is state.States.IN_COMMENT_MULTILINE: # /* ... */

            self._comment_parts.append('\n') # newline

        if not self._first_line:

            self._next_handler.handle_newline()

        else:

            self._first_line = False

        for match in re.finditer(pattern=PATTERN, string=line):

            part = match.group(1)
            #print(self._state, self._string_delim, repr(part))
            if   self._state is state.States.IN_STRING: # "..."

                if part != self._string_delim:

                    self._string_parts.append(part)

                else:

                    self._next_handler.handle_part(part=f'{self._string_delim}{''.join(self._string_parts)}{self._string_delim}')
                    self._string_parts = None
                    self._string_delim = None
                    self._state = state.States.DEFAULT

            elif self._state is state.States.IN_COMMENT_ONELINE: # // ...

                self._comment_parts.append(part)
                # continue, because everything else in this line is part of the comment

            elif self._state is state.States.IN_COMMENT_MULTILINE: 
                
                if part != '*/':

                    self._comment_parts.append(part)

                else:

                    self._next_handler.handle_comment(text=''.join(self._comment_parts))
                    self._comment_parts = None
                    self._state = state.States.DEFAULT

            else:

                if not part.strip(): 
                    
                    self._next_handler.handle_spacing(spacing=part)

                elif part in {'"', '\''} : 
                    
                    self._state = state.States.IN_STRING
                    self._string_delim = part
                    self._string_parts = list()

                elif part == '/*': 
                    
                    self._comment_parts = list()
                    self._state = state.States.IN_COMMENT_MULTILINE

                elif part == '//': 
                    
                    self._comment_parts = list()
                    self._state = state.States.IN_COMMENT_ONELINE

                else:

                    self._next_handler.handle_part(part=part)

    @typing.override
    def handle_eof(self):
        
        self._next_handler.handle_eof()
