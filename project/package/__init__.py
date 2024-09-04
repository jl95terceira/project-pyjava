import io
import re
import typing

from .   import handlers
from .l0 import L0Handler
from .l2 import L2Handler

class StreamParser:

    def __init__(self, handler:handlers.StreamHandler|None=None):

        self._l0 = L0Handler(stream_handler=handler if handler is not None else L2Handler())

    def parse_whole(self, source:str): 

        for line in source.splitlines():

            self.parse(line)

    def parse      (self, line  :str):

        self._l0.handle_line(line)
