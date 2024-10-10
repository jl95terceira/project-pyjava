from . import handlers

class StreamParser:

    def __init__(self, handler:handlers.StreamHandler|None=None):

        self._h  = handler if handler is not None else handlers.l2.L2Handler()
        self._l0 = self._make_l0()

    def _make_l0   (self): return handlers.part.Handler(stream_handler=self._h)

    def parse_whole(self, source:str): 

        for line in source.splitlines():

            self.parse(line)

        self.eof()

    def parse      (self, line  :str): self._l0.handle_line(line)
    def eof        (self):             self._l0.handle_eof ()
