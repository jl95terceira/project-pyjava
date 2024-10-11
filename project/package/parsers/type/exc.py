import builtins

class Exception               (builtins.Exception): pass
class InvalidNameException    (Exception): pass
class ArrayNotAllowedException(Exception): pass
class ArrayNotClosedException (Exception): pass
class EOFException            (Exception): pass
