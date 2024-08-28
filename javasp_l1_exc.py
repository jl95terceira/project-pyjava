import builtins

class Exception               (builtins.Exception): pass
class ReservedWordException   (Exception): pass
class PackageException        (Exception): pass
class ImportException         (Exception): pass
class ClassException          (Exception): pass
class ClassImplementsException(Exception): pass
class AttributeException      (Exception): pass
class MethodException         (Exception): pass
