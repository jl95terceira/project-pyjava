import unittest

from . import *

class Tests(unittest.TestCase): 

    def setUp(self):

        self.tr = TestRegistrator()
        self.th = self.tr.handler(self)

    def test_1(self):

        self.tr.r_package      (model.Package          (name='project.tests.java_files'))
        self.tr.r_import_      (model.Import           (name='java.util.Map'))
        self.tr.r_class_       (model.Class            (name='Test1', access=model.AccessModifiers.PUBLIC))
        self.tr.r_attribute    (model.Attribute        (name='a1', type_name='int'    ,              access=model.AccessModifiers.PRIVATE))
        self.tr.r_attribute    (model.Attribute        (name='a2', type_name='boolean', static=True))
        self.tr.r_attribute    (model.Attribute        (name='a3', type_name='String' ,              access=model.AccessModifiers.PROTECTED))
        self.tr.r_attribute    (model.Attribute        (name='a4', type_name='Object' , static=True, access=model.AccessModifiers.PUBLIC))
        self.tr.r_attribute    (model.Attribute        (name='b1', type_name='int'    ,              access=model.AccessModifiers.PRIVATE    , value=' 123'            , final =True))
        self.tr.r_attribute    (model.Attribute        (name='b2', type_name='boolean', static=True                                          , value=' true'           , final =True))
        self.tr.r_attribute    (model.Attribute        (name='b3', type_name='String' ,              access=model.AccessModifiers.PROTECTED  , value=' "abc"'          , final =False))
        self.tr.r_attribute    (model.Attribute        (name='b4', type_name='Object' , static=True, access=model.AccessModifiers.PUBLIC     , value=' new Object() {}', final =True))
        self.tr.r_static_constr(model.StaticConstructor(body='\n'+8*' '+'System.out.println("Hello, static");\n'+4*' '))
        self.tr.r_constructor  (model.Constructor      (args={'properties':model.Argument(type_name='Map<String,String>')}, body=''))
        self.tr.r_class_end    ()
        # do it
        self.th.test_file('Test1.java')
