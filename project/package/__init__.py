from . import handlers, parsers

class StreamParser:

    def __init__(self, handler:handlers.entity.Handler):

        self._p = parsers.part.Parser(stream_handler=handler)

    def parse_whole(self, source:str): 

        for line in source.splitlines():

            self.parse(line)

        self.eof()

    def parse      (self, line  :str): self._p.handle_line(line)

    def eof        (self):             self._p.handle_eof ()
