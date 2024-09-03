import abc
import dataclasses
import typing
import unittest
from   collections import deque

from ..package import handlers, model

@dataclasses.dataclass
class TestsRegistry:

    def __init__(self):

        self.packages            :dict[int, model.Package]            = list()
        self.imports             :dict[int, model.Import]             = list()
        self.annotations         :dict[int, model.Annotation]         = list()
        self.classes             :dict[int, model.Class]              = list()
        self.class_ends          :dict[int, model.ClassEnd]           = list()
        self.static_constructors :dict[int, model.StaticConstructor]  = list()
        self.constructors        :dict[int, model.Constructor]        = list()
        self.attributes          :dict[int, model.Attribute]          = list()
        self.methods             :dict[int, model.Method]             = list()
        self.enum_values         :dict[int, model.EnumValue]          = list()

class TestRegistrator:

    def __init__(self):

        self._tr = TestsRegistry()
        self._i  = 0

    def _index(self): 
        
        i = self._i
        self._i += 1
        return i
    
    def _register[T](self, registry_getter:typing.Callable[[TestsRegistry],dict[int,T]], x:T):

        registry_getter(self._tr)[self._index()] = x

    def r_package         (self, package        :model.Package)          : self._register(lambda tr: tr.packages            , package)
    def r_import_         (self, import_        :model.Import)           : self._register(lambda tr: tr.imports             , import_)
    def r_annotation      (self, annotation     :model.Annotation)       : self._register(lambda tr: tr.annotations         , annotation)
    def r_class_          (self, class_         :model.Class)            : self._register(lambda tr: tr.classes             , class_)
    def r_class_end       (self)                                         : self._register(lambda tr: tr.class_ends          , model.ClassEnd())
    def r_static_constr   (self, static_constr  :model.StaticConstructor): self._register(lambda tr: tr.static_constructors , static_constr)
    def r_constructor     (self, constr         :model.Constructor)      : self._register(lambda tr: tr.constructors        , constr)
    def r_attribute       (self, attr           :model.Attribute)        : self._register(lambda tr: tr.attributes          , attr)
    def r_method          (self, method         :model.Method)           : self._register(lambda tr: tr.methods             , method)
    def r_enum_value      (self, enum_value     :model.EnumValue)        : self._register(lambda tr: tr.enum_values         , enum_value)

    def handler(self) -> handlers.StreamHandler:

        return TestHandler(tr=self._tr)

class TestHandler(abc.ABC): 

    def __init__(self, tr:TestsRegistry):

        self._tr = tr
        self._i  = 0

    def _test[T](self, registry_getter:typing.Callable[[TestsRegistry],dict[int,T]], y:T):

        r = registry_getter(self._tr)
        i = self._i
        assert i in r
        x = r[i]
        assert x == y
        self._i += 1

    @typing.override
    def handle_package           (self, package         :model.Package)             : self._test(lambda tr: tr.packages             , package)
    @typing.override
    def handle_import            (self, import_         :model.Import)              : self._test(lambda tr: tr.imports              , import_)
    @typing.override
    def handle_annotation        (self, annotation      :model.Annotation)          : self._test(lambda tr: tr.annotations          , annotation)
    @typing.override
    def handle_class             (self, class_          :model.Class)               : self._test(lambda tr: tr.classes              , class_)
    @typing.override
    def handle_class_end         (self, class_end       :model.ClassEnd)            : self._test(lambda tr: tr.class_ends           , class_end)
    @typing.override
    def handle_static_constructor(self, static_constr   :model.StaticConstructor)   : self._test(lambda tr: tr.static_constructors  , static_constr)
    @typing.override
    def handle_constructor       (self, constr          :model.Constructor)         : self._test(lambda tr: tr.constructors         , constr)
    @typing.override
    def handle_attr              (self, attr            :model.Attribute)           : self._test(lambda tr: tr.attributes           , attr)
    @typing.override
    def handle_method            (self, method          :model.Method)              : self._test(lambda tr: tr.methods              , method)
    @typing.override
    def handle_enum_value        (self, enum_value      :model.EnumValue)           : self._test(lambda tr: tr.enum_values          , enum_value)
