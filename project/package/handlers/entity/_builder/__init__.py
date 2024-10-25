import typing

from .    import exc
from ..   import Handler, PackageDeclaration, ImportDeclaration, ClassHeaderDeclaration, InitializerDeclaration, ConstructorDeclaration, AttributeDeclaration, MethodDeclaration
from .... import model

class Builder(Handler):

    def __init__(self):

        self._unit                          = model.Unit()
        self._class_stack:list[model.Class] = list()

    @typing.override
    def handle_package      (self, package_decl:PackageDeclaration):  
        
        if self._unit.package is not None: raise exc.PackageDuplicateException()
        if self._class_stack             : raise exc.PackageInsideClassException()
        self._unit.package = package_decl.name

    @typing.override
    def handle_import       (self, import_decl:ImportDeclaration):  
        
        if self._class_stack              : raise exc.ImportInsideClassException()
        import_dict = (self._unit.imports        if not import_decl.static else \
                       self._unit.imports_static)
        if import_decl.name in import_dict: raise exc.ImportDuplicateException()
        import_dict[import_decl.name] = model.Import()

    @typing.override
    def handle_class        (self, class_decl:ClassHeaderDeclaration):  
        
        class_                                = model.Class(header=class_decl.header)
        class_dict:dict[str,model.Class]|None = None
        if not self._class_stack:

            if class_decl.static: raise exc.StaticRootClassException()
            class_dict = self._unit.classes

        else:

            parent     = self._class_stack[-1]
            class_dict = (parent.members.classes        if not class_decl.static else \
                          parent.members.static_classes)
            
        if class_decl.name in class_dict: raise exc.ClassDuplicateException()
        class_dict[class_decl.name] = class_
        self._class_stack.append(class_)

    @typing.override
    def handle_class_end    (self):  
        
        self._class_stack.pop()

    @typing.override
    def handle_initializer  (self, initializer_decl:InitializerDeclaration): 
        
        if not self._class_stack: raise exc.InitializerOutsideClassException()
        parent = self._class_stack[-1]
        if initializer_decl.static:

            if parent.members.static_initializer is not None: raise exc.StaticInitializerDuplicateException()
            parent.members.static_initializer = initializer_decl.initializer
        
        else:

            if parent.members.initializer is not None: raise exc.InitializerDuplicateException()
            parent.members.initializer = initializer_decl.initializer

    @typing.override
    def handle_constructor  (self, constructor_decl:ConstructorDeclaration):
        
        if not self._class_stack: raise AssertionError()
        parent = self._class_stack[-1]
        parent.members.constructors.append(constructor_decl.constructor)

    @typing.override
    def handle_attribute    (self, attribute_decl:AttributeDeclaration):  
        
        if not self._class_stack: raise exc.AttributeOutsideClassException()
        parent = self._class_stack[-1]
        attributes_dict = (parent.members.attributes        if not attribute_decl.static else \
                           parent.members.static_attributes)
        attributes_dict[attribute_decl.name].append(attribute_decl.attribute)

    @typing.override
    def handle_method       (self, method_decl:MethodDeclaration):
        
        if not self._class_stack: raise exc.MethodOutsideClassException()
        parent = self._class_stack[-1]
        methods_dict = (parent.members.methods        if not method_decl.static else \
                        parent.members.static_methods)
        methods_dict[method_decl.name].append(method_decl.method)

    @typing.override
    def handle_enum_value   (self, enumv_decl:model.EnumValue):  ...
    @typing.override
    def handle_comment      (self, comment:model.Comment): ...
