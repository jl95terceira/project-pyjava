import builtins

class Exception(builtins.Exception): pass
class StopException              (Exception): pass
class EOFException               (Exception): pass
class WildcardNotAllowedException(Exception): pass
class DotDuplicateException      (Exception): pass
