import re

from .    import exc
from .    import state
from ..   import handlers
from ..l1 import L1Handler

PATTERN  = re.compile(f'((?:\\w+)|(?:/\\*)|(?:\\*/)|(?://)|(?:\\\\.)|\\s+|.)')

class L0Handler:

    def __init__(self, stream_handler:handlers.StreamHandler):

        self._next_handler              = L1Handler(stream_handler=stream_handler)
        self._state                     = state.States.DEFAULT
        self._comment_parts:list[str]   = list()
        self._string_parts :list[str]   = list()
        self._first_line                = True

    def handle_line(self, line:str):

        if   self._state is state.States.IN_COMMENT_ONELINE: # // ...

            self._next_handler.handle_comment(text=''.join(self._comment_parts), line=line)
            self._comment_parts.clear()
            self._state = state.States.DEFAULT # no longer in comment, since this is another line

        elif self._state is state.States.IN_COMMENT_MULTILINE: # /* ... */

            self._comment_parts.append('\n') # newline

        if not self._first_line:

            self._next_handler.handle_newline(line=line)

        else:

            self._first_line = False

        for match in re.finditer(pattern=PATTERN, string=line):

            part = match.group(1)
            if   self._state is state.States.IN_STRING: # "..."

                if part != '"':

                    self._string_parts.append(part)

                else:

                    self._next_handler.handle_part(part=f'"{''.join(self._string_parts)}"', line=line)
                    self._string_parts.clear()
                    self._state = state.States.DEFAULT

            elif self._state is state.States.IN_COMMENT_ONELINE: # // ...

                self._comment_parts.append(part)
                # continue, because everything else in this line is part of the comment

            elif self._state is state.States.IN_COMMENT_MULTILINE: 
                
                if part != '*/':

                    self._comment_parts.append(part)

                else:

                    self._next_handler.handle_comment(text=''.join(self._comment_parts), line=line)
                    self._comment_parts.clear()
                    self._state = state.States.DEFAULT

            else:

                if not part.strip(): 
                    
                    self._next_handler.handle_spacing(spacing=part, line=line)

                elif part == '"' : self._state = state.States.IN_STRING
                elif part == '/*': self._state = state.States.IN_COMMENT_MULTILINE
                elif part == '//': self._state = state.States.IN_COMMENT_ONELINE
                else:

                    self._next_handler.handle_part(part=part, line=line)
