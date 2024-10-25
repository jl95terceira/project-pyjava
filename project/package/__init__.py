from . import handlers, parsers

class StreamParser:

    def __init__(self, handler:handlers.entity.Handler):

        self._p = parsers.part.Parser(stream_handler=handler)

    def parse_whole(self, source:str): 

        for line in source.splitlines():

            self.parse_line(line)

        self.eof()

    def parse_line (self, line  :str): self._p.handle_line(line)

    def eof        (self):             self._p.handle_eof ()

class Loader(StreamParser):

    def __init__(self):

        self._builder = handlers.entity.builder.Builder()
        super().__init__(handler=self._builder)

    def get(self): return self._builder.get()

def load(source:str): 
    
    loader = Loader()
    loader.parse_whole(source)
    return loader.get()
