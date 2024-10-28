import builtins

class Exception(builtins.Exception): pass

class PackageDuplicateException             (Exception): pass
class PackageInsideClassException           (Exception): pass
class ImportInsideClassException            (Exception): pass
class StaticRootClassException              (Exception): pass
class ClassDuplicateException               (Exception): pass
class RootClassDuplicateException           (Exception): pass
class InitializerOutsideClassException      (Exception): pass
class StaticInitializerDuplicateException   (Exception): pass
class InitializerDuplicateException         (Exception): pass
class AttributeOutsideClassException        (Exception): pass
class AttributeDuplicateException           (Exception): pass
class MethodOutsideClassException           (Exception): pass
class EnumValueDuplicationException         (Exception): pass
