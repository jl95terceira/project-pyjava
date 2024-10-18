import itertools
import unittest

from . import *
# re-use keyword maps - not pretty (since they are an implementation detail, suggested by the 
# leading '_') but very useful to construct strings to be used in tests as Java source
from ..package.parsers.entity import _ACCESS_MOD_MAP_BY_KEYWORD, \
                                   _FINALITY_TYPE_MAP_BY_KEYWORD, \
                                   _CLASS_TYPE_MAP_BY_KEYWORD

_ACCESS_MOD_MAP_RE    = dict((v,k) for k,v in _ACCESS_MOD_MAP_BY_KEYWORD   .items())
_FINALITY_TYPE_MAP_RE = dict((v,k) for k,v in _FINALITY_TYPE_MAP_BY_KEYWORD.items())
_CLASS_TYPE_MAP_RE    = dict((v,k) for k,v in _CLASS_TYPE_MAP_BY_KEYWORD   .items())

class GeneralTests              (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)

    def test_01(self): self.th.test(';')
    def test_02(self): self.th.test(';;;;;;;;;;;;;;;;;;;;;;;;')
    def test_03(self): self.th.test('')
    @to_fail
    def test_04(self): self.th.test('package hello;')
    @to_fail
    def test_05(self): self.th.test(';package hello;')

class PackageTests              (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)
        self.tr.r_package(model.Package(name='abc.def'))

    def test(self, name='abc.def', end=';'): self.th.test(' '.join(filter(bool, ('package',name,end))))

    def test_correct     (self): self.test()
    @to_fail
    def test_wrong_name  (self): self.test(name='abc.ddf;')
    @to_explode
    def test_no_semicolon(self): self.test(end='')

class ImportTests               (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)
        self.tr.r_import(model.Import(name='foo.bar'))

    def test(self, static=False, name='foo.bar', end=';'): self.th.test(' '.join(filter(bool, ('import','static' if static else '',name,end))))

    def test_correct     (self): self.test()
    @to_fail
    def test_wrong_static(self): self.test(static=True)
    @to_fail
    def test_wrong_name  (self): self.test(name='foo.baz')
    @to_explode
    def test_no_semicolon(self): self.test(end='')

class ImportTestsCombinations   (unittest.TestCase): 

    def setUp(self): self.tr,self.th = gett(self)

    def test(self):

        for i,static in enumerate((True,False,)):

            with self.subTest(i=i):

                self.tr.clear_registry()
                self.th.reset         ()
                self.tr.r_import     (model.Import(name='hello.world', static=static))
                self.th.test          (' '.join(filter(bool, (f'import','static ' if static else '', 'hello.world;'))))

class AnnotationTests           (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)
        self.tr.r_class   (model.Class(name='Foo', annotations=[model.Annotation(name='Log')]))
        self.tr.r_class_end()

    def test_01        (self): self.th.test('@Log class Foo {}'  , end=True)
    @to_fail
    def test_wrong_name(self): self.th.test('@Lag class Foo {}'  , end=True)

class AnnotationTests2          (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)
        self.tr.r_class    (model.Class('Foo', annotations=[model.Annotation(name='DataClass', args=['true', ' 123', ' this.<String, String>get()'])]))
        self.tr.r_class_end()

    def test_01          (self): self.th.test('@DataClass(true, 123, this.<String, String>get()) class Foo {}', end=True)
    @to_fail
    def test_wrong_args  (self): self.th.test('@DataClass(false, 123, this.<String, String>get()) class Foo {}', end=True)
    @to_fail
    def test_wrong_args  (self): self.th.test('@DataCloss(true, 123, this.<String, String>get()) class Foo {}', end=True)
    @to_fail
    def test_wrong_args_2(self): self.th.test('@DataClass(true, 456, this.<String, String>get()) class Foo {}', end=True)
    @to_fail
    def test_wrong_args_2(self): self.th.test('@DataClass(true, 456, this.<String, Integer>get()) class Foo {}', end=True)
    @to_fail
    def test_wrong_args_order(self): self.th.test('@DataClass(123, this.<String, String>get(), true) class Foo {}', end=True)

class ClassTests                (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)
        self.tr.r_class(model.Class(name      ='Foo', 
                                     access    =model.AccessModifiers.PUBLIC, 
                                     inherit  ={model.InheritanceTypes.EXTENDS   : [model.Type(name='Bar')],
                                                 model.InheritanceTypes.IMPLEMENTS: [model.Type(name='Tim'), model.Type(name='Tom', generics=[model.Type(name='Tum')])]}))
        self.tr.r_class_end()

    def test(self, access=model.AccessModifiers.PUBLIC, static=False, type=model.ClassTypes.CLASS, name='Foo', extends:list[model.Type]=[model.Type(name='Bar')], implements:list[model.Type]=[model.Type(name='Tim'),model.Type(name='Tom', generics=[model.Type(name='Tum')]),], end='{}'):

        self.th.test(' '.join(filter(bool, (_ACCESS_MOD_MAP_RE[access], 
                                            'static' if static else '', 
                                            _CLASS_TYPE_MAP_RE[type], 
                                            name, 
                                            'extends'   , ', '.join(t.source() for t in extends), 
                                            'implements', ', '.join(t.source() for t in implements), end))))

    def test_correct            (self): self.test()
    @to_fail
    def test_wrong_access       (self): self.test(access=model.AccessModifiers.DEFAULT)
    @to_fail
    def test_wrong_static       (self): self.test(static=True)
    @to_fail
    def test_wrong_type         (self): self.test(type=model.ClassTypes.INTERFACE)
    @to_fail
    def test_wrong_name         (self): self.test(name='Fuu')
    @to_fail
    def test_wrong_extends      (self): self.test(extends   =[model.Type(name='Baz')])
    @to_fail
    def test_wrong_implements   (self): self.test(implements=[model.Type(name='Tim'), model.Type(name='Tam', generics=[model.Type(name='Tum')])])
    @to_fail
    def test_wrong_implements_2 (self): self.test(implements=[model.Type(name='Tim')])
    @to_fail
    def test_wrong_implements_3 (self): self.test(implements=[model.Type(name='Tom', generics=[model.Type(name='Tum')])])
    @to_explode
    def test_no_closer          (self): self.test(end='{')
    @to_explode
    def test_wrong_closer       (self): self.test(end='{{')
    @to_explode
    def test_wrong_opener       (self): self.test(end='}')

class ClassTestsCombinations    (unittest.TestCase): 

    def setUp(self):

        self.tr,self.th = gett(self)

    def test(self):

        for i,(access   , 
               static   ,
               finality ,
               type     ) in enumerate(itertools.product(model.AccessModifiers.values(),
                                                         (True,False,),
                                                         model.FinalityTypes  .values(),
                                                         model.ClassTypes     .values())):

            with self.subTest(i=i):

                self.tr.clear_registry()
                self.th.reset         ()
                self.tr.r_class      (model.Class(name='Hello', access=access, static=static, finality=finality, type=type))
                self.tr.r_class_end   ()
                self.th.test          (' '.join(filter(bool, (_ACCESS_MOD_MAP_RE[access], 
                                                              'static' if static else '', 
                                                              _FINALITY_TYPE_MAP_RE[finality], 
                                                              _CLASS_TYPE_MAP_RE[type], 'Hello {}'))))
