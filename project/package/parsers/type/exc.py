import builtins

class Exception(builtins.Exception): pass
class ArrayNotAllowedException      (Exception): pass
class ArrayNotClosedException       (Exception): pass
class AnnotationsNotAllowedException(Exception): pass
class EOFException                  (Exception): pass
class GenericsDuplicateException    (Exception): pass
