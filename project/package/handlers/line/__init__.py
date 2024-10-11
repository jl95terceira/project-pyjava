import abc

class Handler(abc.ABC):

    @abc.abstractmethod
    def handle_line                 (self, line:str): ...
    @abc.abstractmethod
    def handle_eof                  (self): ...