import builtins
import dataclasses
import functools
import os.path
import typing
import unittest

from ..package.handlers import entity

from ..package import model, StreamParser

_DEBUG = 0
_JAVA_FILES_PATH = 'java_files'

@functools.wraps(builtins.print)
def print(*aa,**kaa):

    if not _DEBUG: return
    builtins.print(*aa,**kaa)

@dataclasses.dataclass
class _TestsRegistry:

    def __init__(self):

        self.packages           :dict[int, model.Package]           = dict()
        self.imports            :dict[int, model.Import]            = dict()
        self.classes            :dict[int, model.Class]             = dict()
        self.class_ends         :dict[int, None]                    = dict()
        self.initializers       :dict[int, model.Initializer]       = dict()
        self.constructors       :dict[int, model.Constructor]       = dict()
        self.attributes         :dict[int, model.Attribute]         = dict()
        self.methods            :dict[int, model.Method]            = dict()
        self.enum_values        :dict[int, model.EnumValue]         = dict()
        self.ainterfaces        :dict[int, model.AInterface]        = dict()
        self.comments           :dict[int, model.Comment]           = dict()
        self.a                  :list[typing.Any]                   = list()

    def clear(self): 
        
        self.packages           .clear()
        self.imports            .clear()
        self.classes            .clear()
        self.class_ends         .clear()
        self.initializers       .clear()
        self.constructors       .clear()
        self.attributes         .clear()
        self.methods            .clear()
        self.enum_values        .clear()
        self.comments           .clear()
        self.a                  .clear()

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

    def r_package         (self, package        :model.Package)         : self._register(lambda tr: tr.packages     , package)
    def r_import          (self, import_        :model.Import)          : self._register(lambda tr: tr.imports      , import_)
    def r_class           (self, class_         :model.Class)           : self._register(lambda tr: tr.classes      , class_)
    def r_class_end       (self)                                        : self._register(lambda tr: tr.class_ends   , None)
    def r_initializer     (self, initializer    :model.Initializer)     : self._register(lambda tr: tr.initializers , initializer)
    def r_constructor     (self, constr         :model.Constructor)     : self._register(lambda tr: tr.constructors , constr)
    def r_attribute       (self, attr           :model.Attribute)       : self._register(lambda tr: tr.attributes   , attr)
    def r_method          (self, method         :model.Method)          : self._register(lambda tr: tr.methods      , method)
    def r_enum_value      (self, enum_value     :model.EnumValue)       : self._register(lambda tr: tr.enum_values  , enum_value)
    def r_ainterface      (self, ainterface     :model.AInterface)      : self._register(lambda tr: tr.ainterfaces  , ainterface)
    def r_comment         (self, comment        :model.Comment)         : self._register(lambda tr: tr.comments     , comment)

    def clear_registry(self): 
        
        self._tr.clear()
        self._i = 0

    def handler(self, tc:unittest.TestCase):

        return _TestHandler(tr=self._tr, tc=tc)

class _TestHandler(entity.Handler): 

    def __init__(self, tr:_TestsRegistry, tc:unittest.TestCase):

        self._tr         = tr
        self._tc         = tc
        self._i:int|None = None
        self._parser     = StreamParser(self)
        self.reset()

    def _test[T](self, registry_getter:typing.Callable[[_TestsRegistry],dict[int,T]], got:T):

        i   = self._i
        MSG = lambda: f'No more entities expected at position {i} and beyond\n  Got: {got}'
        self._tc.assertLess (i  , len(self._tr.a), msg=MSG())
        self._i += 1
        exo = self._tr.a[i]
        reg = registry_getter(self._tr)
        MSG = lambda: '\n'.join((f'Unexpected type of entity at position {i}',
                                 f'  Expected: {self._tr.a[i]}',
                                 f'  Got     : {got}',))
        self._tc.assertIn   (i  , reg            , msg=MSG())
        exo = reg[i]
        MSG = lambda: '\n'.join((f'Attributes different than expected for entity at position {i}',
                                 f'  Expected: {exo}',
                                 f'  Got     : {got}',))
        self._tc.assertEqual(exo, got            , msg=MSG())

    def reset(self):

        self._i      = 0
        self._parser = StreamParser(self)

    def test_file(self, fn:str, pre_reset=True, end=True):

        print(f'Testing file   : {repr(fn)}', flush=True)
        if pre_reset: self.reset()
        with open(os.path.join(os.path.split(__file__)[0], _JAVA_FILES_PATH, fn), mode='r', encoding='utf-8') as f:

            self._parser.parse_whole(f.read())

        if end: self.end()

    def test     (self, line:str, end=True):

        print(f'Got line       : {repr(line)}', flush=True)
        self._parser.parse(line)
        if end: 
            
            self._parser.eof()
            self        .end()

    def end(self):

        self._tc.assertEqual(self._i, len(self._tr.a), msg=f'Expected no more entities to be process but there are {len(self._tr.a) - self._i} remaining')

    @typing.override
    def handle_package          (self, package         :model.Package)      : self._test(lambda tr: tr.packages     , package)
    @typing.override
    def handle_import           (self, import_         :model.Import)       : self._test(lambda tr: tr.imports      , import_)
    @typing.override
    def handle_class            (self, class_          :model.Class)        : self._test(lambda tr: tr.classes      , class_)
    @typing.override
    def handle_class_end        (self)                                      : self._test(lambda tr: tr.class_ends   , None)
    @typing.override
    def handle_initializer      (self, initializer     :model.Initializer)  : self._test(lambda tr: tr.initializers , initializer)
    @typing.override
    def handle_constructor      (self, constr          :model.Constructor)  : self._test(lambda tr: tr.constructors , constr)
    @typing.override
    def handle_attr             (self, attr            :model.Attribute)    : self._test(lambda tr: tr.attributes   , attr)
    @typing.override
    def handle_method           (self, method          :model.Method)       : self._test(lambda tr: tr.methods      , method)
    @typing.override
    def handle_enum_value       (self, enum_value      :model.EnumValue)    : self._test(lambda tr: tr.enum_values  , enum_value)
    @typing.override
    def handle_ainterface       (self, ainterface      : model.AInterface)  : self._test(lambda tr: tr.ainterfaces  , ainterface)
    @typing.override
    def handle_comment          (self, comment         :model.Comment)      : self._test(lambda tr: tr.comments     , comment)

def to_fail(f):

    def g(*a,**ka):

        try                  : f(*a,**ka)
        except AssertionError: pass
        else                 : raise AssertionError('test should have failed')
    
    return g

def to_explode(f):

    def g(*a,**ka):

        try                  : f(*a,**ka)
        except AssertionError: raise AssertionError('test should have exploded (not with an assertion error)')
        except               : pass
        else                 : raise AssertionError('test should have exploded')
    
    return g

def gett(tc:unittest.TestCase): 

    tr = TestRegistrator()
    return tr,tr.handler(tc)

class Meta(unittest.TestCase):

    def test_to_pass(self): self.assertTrue(True)
    @to_fail
    def test_to_fail(self): self.assertTrue(False)
