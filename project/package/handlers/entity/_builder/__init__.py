import typing

from .    import exc
from ..   import Handler, PackageDeclaration, ImportDeclaration, ClassHeaderDeclaration
from .... import model

class Builder(Handler):

    def __init__(self):

        self._unit                          = model.Unit()
        self._class_stack:list[model.Class] = list()

    @typing.override
    def handle_package      (self, package:PackageDeclaration):  
        
        if self._unit.package is not None: raise exc.PackageDuplicateException()
        if self._class_stack             : raise exc.PackageInsideClassException()
        self._unit.package = package.name

    @typing.override
    def handle_import       (self, import_:ImportDeclaration):  
        
        if self._class_stack          : raise exc.ImportInsideClassException()
        import_dict = (self._unit.imports        if not import_.static else \
                       self._unit.imports_static)
        if import_.name in import_dict: raise exc.ImportDuplicateException()
        import_dict[import_.name] = model.Import()

    @typing.override
    def handle_class        (self, class_:ClassHeaderDeclaration):  
        
        clas                                 = model.Class(header=class_.header)
        clas_dict:dict[str,model.Class]|None = None
        if not self._class_stack:

            if class_.static: raise exc.StaticRootClassException()
            clas_dict = self._unit.classes

        else:

            parent = self._class_stack[-1]
            clas_dict = (parent.members.classes        if not class_.static else \
                         parent.members.static_classes)
            
        if class_.name in clas_dict: raise exc.ClassDuplicateException()
        clas_dict[class_.name] = clas
        self._class_stack.append(clas)

    @typing.override
    def handle_class_end    (self):  
        
        self._class_stack.pop()

    @typing.override
    def handle_initializer  (self, initializer:model.Initializer): 
        
        if not self._class_stack: raise exc.InitializerOutsideClassException()
        parent = self._class_stack[-1]
        if initializer.static:

            if parent.members.initializer is not None: raise exc.StaticInitializerDuplicateException()
            raise NotImplementedError() #TO-DO
        
        else:

            raise NotImplementedError() #TO-DO

    @typing.override
    def handle_constructor  (self, constr:model.Constructor):  ...
    @typing.override
    def handle_attr         (self, attr:model.Attribute):  ...
    @typing.override
    def handle_method       (self, method:model.Method):  ...
    @typing.override
    def handle_enum_value   (self, enum:model.EnumValue):  ...
    @typing.override
    def handle_comment      (self, comment:model.Comment): ...
