import re

import javasp_l0_exc as exc
from javasp_l1 import L1Handler

PATTERN_WORD_BEGIN = '^|(?<!\\w)'
PATTERN_WORD_END   = '$|(?!\\w)'
PATTERN_WORD       = '(?:[\\w\\.:\\*])+'
PATTERN            = re.compile(f'((?:{PATTERN_WORD_BEGIN})(?:{PATTERN_WORD})(?:{PATTERN_WORD_END})|[^\\s])|(\\s+)')

class L0Handler:

    def __init__(self):

        self._next_handler = L1Handler()

    def handle_line(self, line:str):

        string_parts:list[str] = list()
        for match in re.finditer(pattern=PATTERN, string=line):

            g = match.group(1)
            if g is None: continue
            if g.startswith('"'):

                if string_parts: 
                    
                    if g != '"': 
                        
                        raise exc.BadStringException(repr(''.join((*string_parts, g))))
                
                if   g.split('\\\\')[-1] == '"': pass
                else:

                    string_parts.append(g)
                    continue

            else:

                if not string_parts: pass
                elif g.split('\\\\')[-1] == '"': 
                
                    g = ''.join((*string_parts, g))

                else:

                    string_parts.append(g)
                    continue

            self._next_handler.handle_part(part=g, line=line)

