import abc as _abc
    
class Handler(_abc.ABC):

    @_abc.abstractmethod
    def handle_line                 (self, line:str): ...
    @_abc.abstractmethod
    def handle_eof                  (self): ...

