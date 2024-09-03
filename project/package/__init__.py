import re
import typing

from .l0 import L0Handler
from .l2 import L2Handler

def parse_whole(source:str):

    parse_by_line(map(lambda match: match.group(0), re.finditer(pattern='(?m)^(.*)$', string=source)))

def parse_by_line(lines:typing.Iterable[str]):

    l0 = L0Handler(stream_handler=L2Handler())
    for line in lines:

        l0.handle_line(line)

