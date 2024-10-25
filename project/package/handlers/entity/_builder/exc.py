import builtins

class Exception(builtins.Exception): pass

class PackageDuplicateException             (Exception): pass
class PackageInsideClassException           (Exception): pass
class ImportDuplicateException              (Exception): pass
class ImportInsideClassException            (Exception): pass
class StaticRootClassException              (Exception): pass
class ClassDuplicateException               (Exception): pass
class InitializerOutsideClassException      (Exception): pass
class StaticInitializerDuplicateException   (Exception): pass
