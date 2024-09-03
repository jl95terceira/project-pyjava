import re
import typing

from .l0 import L0Handler

def parse_whole(source:str):

    parse_by_line(map(lambda match: match.group(0), re.finditer(pattern='(?m)^(.*)$', string=source)))

def parse_by_line(lines:typing.Iterable[str]):

    l0 = L0Handler()
    for line in lines:

        l0.handle_line(line)

