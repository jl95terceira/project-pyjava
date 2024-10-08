from .            import handlers
from .handlers.l0 import L0Handler
from .handlers.l2 import L2Handler

class StreamParser:

    def __init__(self, handler:handlers.StreamHandler|None=None):

        self._h  = handler if handler is not None else L2Handler()
        self._l0 = self._make_l0()

    def _make_l0   (self): return L0Handler(stream_handler=self._h)

    def parse_whole(self, source:str): 

        for line in source.splitlines():

            self.parse(line)

    def parse      (self, line  :str):

        self._l0.handle_line(line)
