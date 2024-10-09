import builtins

class Exception(builtins.Exception): pass
class InvalidOpenException   (Exception): pass
class AfterSeparatorException(Exception): pass
class EOFException           (Exception): pass