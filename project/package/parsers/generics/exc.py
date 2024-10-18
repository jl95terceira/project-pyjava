import builtins

class Exception(builtins.Exception): pass
class BadOpeningException     (Exception): pass
class StopException           (Exception): pass
class TypeNameInvalidException(Exception): pass
class EOFException            (Exception): pass
