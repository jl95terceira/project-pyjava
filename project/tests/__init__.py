import dataclasses
import os.path
import typing
import unittest

from ..package import handlers, model, StreamParser

@dataclasses.dataclass
class _TestsRegistry:

    def __init__(self):

        self.packages            :dict[int, model.Package]            = dict()
        self.imports             :dict[int, model.Import]             = dict()
        self.annotations         :dict[int, model.Annotation]         = dict()
        self.classes             :dict[int, model.Class]              = dict()
        self.class_ends          :dict[int, model.ClassEnd]           = dict()
        self.static_constructors :dict[int, model.StaticConstructor]  = dict()
        self.constructors        :dict[int, model.Constructor]        = dict()
        self.attributes          :dict[int, model.Attribute]          = dict()
        self.methods             :dict[int, model.Method]             = dict()
        self.enum_values         :dict[int, model.EnumValue]          = dict()
        self.comments            :dict[int, model.Comment]            = dict()
        self.a                   :list[typing.Any]                    = list()

class TestRegistrator:

    def __init__(self):

        self._tr = _TestsRegistry()
        self._i  = 0

    def _index(self): 
        
        i = self._i
        self._i += 1
        return i
    
    def _register[T](self, registry_getter:typing.Callable[[_TestsRegistry],dict[int,T]], x:T):

        registry_getter(self._tr)[self._index()] = x
        self._tr.a.append(x)

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
    def r_comment         (self, comment        :model.Comment)          : self._register(lambda tr: tr.comments            , comment)

    def handler(self, tc:unittest.TestCase):

        return _TestHandler(tr=self._tr, tc=tc)

class _TestHandler(handlers.StreamHandler): 

    def __init__(self, tr:_TestsRegistry, tc:unittest.TestCase):

        self._tr         = tr
        self._tc         = tc
        self._i:int|None = None

    def _test[T](self, registry_getter:typing.Callable[[_TestsRegistry],dict[int,T]], y:T):

        i = self._i
        print(f'Got at position {i}: {type(y).__name__}')
        self._tc.assertLess (i, len(self._tr.a), msg=f'no more entities expected at position {i} and beyond\n  Got: {y}')
        r = registry_getter(self._tr)
        self._tc.assertIn   (i, r              , msg=f'unexpected type of entity at position {i}\n  Expected: {self._tr.a[i]}\n  Got     : {y}')
        x = r[i]
        self._tc.assertEqual(x, y              , msg=f'attributes different than expected for entity at position {i}\n  Expected: {x}\n  Got     : {y}')
        self._i += 1

    def begin(self):

        self._i = 0

    def test_file(self, fn:str):

        self.begin()
        with open(os.path.join(os.path.split(__file__)[0], 'java_files', fn), mode='r', encoding='utf-8') as f:

            StreamParser(handler=self).parse_whole(f.read())

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
    @typing.override
    def handle_comment           (self, comment         :model.Comment)             : self._test(lambda tr: tr.comments             , comment)
