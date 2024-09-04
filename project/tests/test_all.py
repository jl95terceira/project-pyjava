import unittest

from .. import package as java
from .         import *

class Tests(unittest.TestCase): 
    
    def test_1(self):

        tr = TestRegistrator()
        tr.r_package      (model.Package          (name='project.tests.java_files'))
        tr.r_import_      (model.Import           (name='java.util.Map'))
        tr.r_class_       (model.Class            (name='Test1', access=model.AccessModifiers.PUBLIC))
        tr.r_attribute    (model.Attribute        (name='a1', type_name='int'    ,              access=model.AccessModifiers.PRIVATE))
        tr.r_attribute    (model.Attribute        (name='a2', type_name='boolean', static=True))
        tr.r_attribute    (model.Attribute        (name='a3', type_name='String' ,              access=model.AccessModifiers.PROTECTED))
        tr.r_attribute    (model.Attribute        (name='a4', type_name='Object' , static=True, access=model.AccessModifiers.PUBLIC))
        tr.r_attribute    (model.Attribute        (name='b1', type_name='int'    ,              access=model.AccessModifiers.PRIVATE    , value=' 123'            , final =True))
        tr.r_attribute    (model.Attribute        (name='b2', type_name='boolean', static=True                                          , value=' true'           , final =True))
        tr.r_attribute    (model.Attribute        (name='b3', type_name='String' ,              access=model.AccessModifiers.PROTECTED  , value=' "abc"'          , final =False))
        tr.r_attribute    (model.Attribute        (name='b4', type_name='Object' , static=True, access=model.AccessModifiers.PUBLIC     , value=' new Object() {}', final =True))
        tr.r_static_constr(model.StaticConstructor(body=''))
        tr.r_constructor  (model.Constructor      (args={'properties':model.Argument(type_name='Map<String,String>')}, body=''))
        tr.r_class_end    ()
        tr.handler(self).test_file('Test1.java')
