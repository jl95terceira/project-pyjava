import abc
import dataclasses
import typing

from ..package import model

@dataclasses.dataclass
class TestsRegistry:

    def __init__(self):

        self.packages            :list[tuple[int, model.Package]]            = list()
        self.imports             :list[tuple[int, model.Import]]             = list()
        self.annotations         :list[tuple[int, model.Annotation]]         = list()
        self.classes             :list[tuple[int, model.Class]]              = list()
        self.class_ends          :list[tuple[int, model.ClassEnd]]           = list()
        self.static_constructors :list[tuple[int, model.StaticConstructor]]  = list()
        self.constructors        :list[tuple[int, model.Constructor]]        = list()
        self.attributes          :list[tuple[int, model.Attribute]]          = list()
        self.methods             :list[tuple[int, model.Method]]             = list()
        self.enum_values         :list[tuple[int, model.EnumValue]]          = list()

class TestRegistrator:

    def __init__(self):

        self._tr = TestsRegistry()
        self._i  = 0

    def _indexed[T](self, x:T, l:list[tuple[int,T]]): 
        
        t = (self._i,x,)
        self._i += 1
        return t
    
    def _registrator[T](registry_getter:typing.Callable[[TestsRegistry],list[tuple[int,T]]]):

        def g(f):

            def h(self:'TestRegistrator', x:T):

                registry_getter(self._tr).append(self._indexed(x))

            return h
        
        return g
    
    def _registrator_const[T](registry_getter:typing.Callable[[TestsRegistry],list[tuple[int,T]]], const:T):

        def g(f):

            def h(self:'TestRegistrator'):

                registry_getter(self._tr).append(self._indexed(const))

            return h
        
        return g
    
    @_registrator(lambda tr: tr.packages)
    def package         (self): pass
    @_registrator(lambda tr: tr.imports)
    def import_         (self): pass
    @_registrator(lambda tr: tr.annotations)
    def annotation      (self): pass
    @_registrator(lambda tr: tr.classes)
    def class_          (self): pass
    @_registrator_const(lambda tr: tr.class_ends, const=model.ClassEnd)
    def class_end       (self): pass
    @_registrator(lambda tr: tr.static_constructors)
    def static_constr   (self): pass
    @_registrator(lambda tr: tr.constructors)
    def constructor     (self): pass
    @_registrator(lambda tr: tr.attributes)
    def attribute       (self): pass
    @_registrator(lambda tr: tr.methods)
    def method          (self): pass
    @_registrator(lambda tr: tr.enum_values)
    def enum_value      (self): pass
