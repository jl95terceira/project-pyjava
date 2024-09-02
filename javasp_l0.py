import re

import javasp_l0_exc   as exc
import javasp_l0_state as state
from javasp_l1 import L1Handler

PATTERN_CHARACTER  = '\\w'
PATTERN_WORD       = f'(?:^|(?<!{PATTERN_CHARACTER})){PATTERN_CHARACTER}+(?:$|(?!{PATTERN_CHARACTER}))'
PATTERN            = re.compile(f'((?:{PATTERN_WORD})|(?:/\\*)|(?:\\*/)|(?://)|\\s+|.)')

class L0Handler:

    def __init__(self):

        self._next_handler              = L1Handler()
        self._state                     = state.States.DEFAULT
        self._comment_parts:list[str]   = list()
        self._first_line                = True

    def handle_line(self, line:str):

        # parsing a comment?
        if   self._state is state.States.IN_COMMENT_ONELINE: # // ...

            self._comment_parts.append('\n') # newline
            self._next_handler.handle_comment(comment=''.join(self._comment_parts), line=line)
            self._state = state.States.DEFAULT # no longer in comment, since this is another line

        elif self._state is state.States.IN_COMMENT_MULTILINE: # /* ... */

            self._comment_parts.append('\n') # newline

        # at 1st line? 
        if not self._first_line:

            self._next_handler.handle_newline(line=line)

        else:

            self._first_line = False

        for match in re.finditer(pattern=PATTERN, string=line):

            part = match.group(1)
            if self._state is state.States.IN_COMMENT_ONELINE:

                self._comment_parts.append(part)
                # continue, because everything else in this line is part of the comment

            elif self._state is state.States.IN_COMMENT_MULTILINE: 
                
                if part != '*/':

                    self._comment_parts.append(part)

                else:

                    self._state = state.States.DEFAULT
                    self._next_handler.handle_comment(comment=''.join(self._comment_parts), line=line)

            else:

                if not part.strip(): 
                    
                    self._next_handler.handle_spacing(spacing=part, line=line)

                elif part == '/*': self._state = state.States.IN_COMMENT_MULTILINE
                elif part == '//': self._state = state.States.IN_COMMENT_ONELINE
                else:

                    self._next_handler.handle_part(part=part, line=line)
