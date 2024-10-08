import unittest

from . import *

class Tests(unittest.TestCase): 

    def setUp(self):

        self.tr = TestRegistrator()
        self.th = self.tr.handler(self)

    def test_1(self):

        self.tr.r_package      (model.Package          (name='project.tests.java_files'))
        self.tr.r_import_      (model.Import           (name='java.util.Map'))
        self.tr.r_class_       (model.Class            (name='Test1'                                                        , access=model.AccessModifiers.PUBLIC))
        self.tr.r_attribute    (model.Attribute        (name='a1', type=model.Type('int')                                   , access=model.AccessModifiers.PRIVATE))
        self.tr.r_attribute    (model.Attribute        (name='a2', type=model.Type('boolean')               , static=True))
        self.tr.r_attribute    (model.Attribute        (name='a3', type=model.Type('String', is_array=True)                 , access=model.AccessModifiers.PROTECTED))
        self.tr.r_attribute    (model.Attribute        (name='a4', type=model.Type('Object')                , static=True   , access=model.AccessModifiers.PUBLIC))
        self.tr.r_attribute    (model.Attribute        (name='b1', type=model.Type('int')                   , static=True   , access=model.AccessModifiers.PRIVATE      , value=' 123'           , final =True))
        self.tr.r_attribute    (model.Attribute        (name='b2', type=model.Type('boolean')                                                                           , value='   true'        , final =True))
        self.tr.r_attribute    (model.Attribute        (name='b3', type=model.Type('String')                                , access=model.AccessModifiers.PROTECTED    , value='  "abc"'        , final =False))
        self.tr.r_attribute    (model.Attribute        (name='b4', type=model.Type('Object', is_array=True) , static=True   , access=model.AccessModifiers.PUBLIC       , value=' new Object[]{}', final =True))
        self.tr.r_static_constr(model.StaticConstructor(body='\n'+8*' '+'System.out.println("Hello, static");\n'+4*' '))
        self.tr.r_constructor  (model.Constructor      (access=model.AccessModifiers.PUBLIC,  args={'properties':model.Argument(type=model.Type('Map'    , generics='<String,String>')),
                                                                                                    'awesome'   :model.Argument(type=model.Type('Boolean'))}, body=''))
        self.tr.r_constructor  (model.Constructor      (access=model.AccessModifiers.PRIVATE, args={'data'      :model.Argument(type=model.Type('byte'   , is_array=True))}, body=f'\n{8*' '}Test1(null, false);\n{4*' '}'))
        self.tr.r_constructor  (model.Constructor      (access=model.AccessModifiers.DEFAULT, args={}, body=f''))
        self.tr.r_class_end    ()
        # do it
        self.th.test_file('Test1.java')
