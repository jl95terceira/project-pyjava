import abc

from ... import handlers

class Handler(handlers.line.Handler):

    @abc.abstractmethod
    def handle_part                 (self, part:str): ...
    @abc.abstractmethod
    def handle_comment              (self, text:str): ...
    @abc.abstractmethod
    def handle_spacing              (self, spacing:str): ...
    @abc.abstractmethod
    def handle_newline              (self): ...