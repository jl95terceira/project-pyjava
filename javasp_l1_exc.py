import builtins

class Exception(builtins.Exception): pass

class AccessModifierRepeatedException   (Exception): pass
class AttributeException                (Exception): pass
class BodyNotOpeningWithBraceException  (Exception): pass
class ClassException                    (Exception): pass
class ClassImplementsException          (Exception): pass
class ClassTypeRepeatedException        (Exception): pass
class FinalityRepeatedException         (Exception): pass
class ImportException                   (Exception): pass
class MethodException                   (Exception): pass
class MethodOrConstructorException      (Exception): pass
class PackageException                  (Exception): pass
class ReservedWordException             (Exception): pass
class StaticRepeatedException           (Exception): pass
