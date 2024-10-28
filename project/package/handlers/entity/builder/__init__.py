from   dataclasses import dataclass, field
import typing

from .    import exc
from ..   import Handler, PackageDeclaration, ImportDeclaration, ClassHeaderDeclaration, InitializerDeclaration, ConstructorDeclaration, AttributeDeclaration, MethodDeclaration, EnumValueDeclaration
from .... import model, util

DEBUG = 0

@dataclass
class _ClassStackElement:

    class_:model.Class = field()
    name  :str         = field()

class _EntityType(util.Named): pass
class _EntityTypes:

    PACKAGE     = _EntityType(name='package')
    IMPORT      = _EntityType(name='import')
    CLASS       = _EntityType(name='class')
    CLASS_END   = _EntityType(name='class end')
    INITIALIZER = _EntityType(name='initializer')
    CONSTRUCTOR = _EntityType(name='constructor')
    ATTRIBUTE   = _EntityType(name='attribute')
    METHOD      = _EntityType(name='method')
    ENUMVALUE   = _EntityType(name='enum value')

class _Handler(typing.Protocol):

    def __call__(self:'Builder', *aa, **kaa): ...

class Builder(Handler):

    def __init__(self):

        self._unit                                  = model.Unit()
        self._class_stack :list[_ClassStackElement] = list()
        self._type_of_prev:_EntityType|None         = None
        self._enum_prev   :model.EnumValue|None     = None

    def _handled(et:_EntityType):

        def _f(f:_Handler):

            def _g(self:'Builder', *aa, **kaa):

                if DEBUG: print(et, *aa, **kaa)
                f(self, *aa, **kaa)
                self._type_of_prev = et

            return _g
        
        return _f

    @typing.override
    @_handled(_EntityTypes.PACKAGE)
    def handle_package      (self, package_decl:PackageDeclaration):  
        
        if self._unit.package is not None: raise exc.PackageDuplicateException  (self._unit.package)
        if self._class_stack             : raise exc.PackageInsideClassException(self._class_stack[-1].name)
        self._unit.package = package_decl.name

    @typing.override
    @_handled(_EntityTypes.IMPORT)
    def handle_import       (self, import_decl:ImportDeclaration):  
        
        if self._class_stack              : raise exc.ImportInsideClassException(self._class_stack[-1].name)
        import_dict = (self._unit.imports        if not import_decl.static else \
                       self._unit.imports_static)
        import_dict[import_decl.name] = model.Import()

    @typing.override
    @_handled(_EntityTypes.CLASS)
    def handle_class        (self, class_decl:ClassHeaderDeclaration):  
        
        class_                    = model.Class(header=class_decl.header)
        class_reg:typing.Callable[[str|None, model.Class],None] \
                                  = None
        if not self._class_stack:

            if class_decl.static: raise exc.StaticRootClassException(class_decl.name)
            if class_decl.name in self._unit.classes: raise exc.RootClassDuplicateException(class_decl.name)
            class_reg = self._unit.classes.__setitem__

        elif class_decl.name is None and self._type_of_prev is _EntityTypes.ENUMVALUE:

            class_reg = _EnumValueSubclassAssigner(self._enum_prev).__call__

        else:

            parent     = self._class_stack[-1].class_
            class_dict = (parent.members.classes        if not class_decl.static else \
                          parent.members.static_classes)
            if class_decl.name in class_dict: raise exc.ClassDuplicateException(class_decl.name)
            class_reg  = class_dict.__setitem__
            
        class_reg(class_decl.name, class_)
        self._class_stack.append(_ClassStackElement(name=class_decl.name, class_=class_,))

    @typing.override
    @_handled(_EntityTypes.CLASS_END)
    def handle_class_end    (self):  
        
        self._class_stack.pop()

    @typing.override
    @_handled(_EntityTypes.INITIALIZER)
    def handle_initializer  (self, initializer_decl:InitializerDeclaration): 
        
        if not self._class_stack: raise exc.InitializerOutsideClassException()
        parent = self._class_stack[-1].class_
        if initializer_decl.static:

            if parent.members.static_initializer is not None: raise exc.StaticInitializerDuplicateException()
            parent.members.static_initializer = initializer_decl.initializer
        
        else:

            if parent.members.initializer is not None: raise exc.InitializerDuplicateException()
            parent.members.initializer = initializer_decl.initializer

    @typing.override
    @_handled(_EntityTypes.CONSTRUCTOR)
    def handle_constructor  (self, constructor_decl:ConstructorDeclaration):
        
        if not self._class_stack: raise AssertionError('constructor outside class')
        parent = self._class_stack[-1].class_
        parent.members.constructors.append(constructor_decl.constructor)

    @typing.override
    @_handled(_EntityTypes.ATTRIBUTE)
    def handle_attribute    (self, attribute_decl:AttributeDeclaration):  
        
        if not self._class_stack: raise exc.AttributeOutsideClassException(attribute_decl.name)
        parent = self._class_stack[-1].class_
        attributes_dict = (parent.members.attributes        if not attribute_decl.static else \
                           parent.members.static_attributes)
        if attribute_decl.name in attributes_dict: raise exc.AttributeDuplicateException(attribute_decl.name)
        attributes_dict[attribute_decl.name] = attribute_decl.attribute

    @typing.override
    @_handled(_EntityTypes.METHOD)
    def handle_method       (self, method_decl:MethodDeclaration):
        
        if not self._class_stack: raise exc.MethodOutsideClassException(method_decl.name)
        parent = self._class_stack[-1].class_
        methods_dict = (parent.members.methods        if not method_decl.static else \
                        parent.members.static_methods)
        methods_dict[method_decl.name].append(method_decl.method)

    @typing.override
    @_handled(_EntityTypes.ENUMVALUE)
    def handle_enum_value   (self, enumvalue_decl:EnumValueDeclaration):  
        
        if not self._class_stack: raise AssertionError(f'enum value {repr(enumvalue_decl.name)} outside class')
        parent = self._class_stack[-1].class_
        if enumvalue_decl.name in parent.members.enumvalues: raise exc.EnumValueDuplicationException(enumvalue_decl.name)
        parent.members.enumvalues[enumvalue_decl.name] = enumvalue_decl.enumvalue
        self._enum_prev = enumvalue_decl.enumvalue

    @typing.override
    def handle_comment      (self, comment:model.Comment): pass #TO-DO

    def get(self): return self._unit

@dataclass
class _EnumValueSubclassAssigner:

    _enumvalue:model.EnumValue = field()

    def __call__(self, name:str|None, class_:model.Class):

        if name is not None: raise AssertionError(f'name of enum value subclass is not None: {repr(name)}')
        self._enumvalue.subclass = class_
