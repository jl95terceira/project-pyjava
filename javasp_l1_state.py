import javasp_util as util

class State(util.Named): pass
class States:

    BEGIN                       = State('')
    PACKAGE                     = State('Package')
    IMPORT                      = State('Import')
    ANNOTATION                  = State('Annotation')
    CLASS_BEGIN                 = State('Class')
    CLASS_AFTER_NAME            = State('Class After-Name')
    CLASS_EXTENDS               = State('Class Extends')
    CLASS_IMPLEMENTS            = State('Class Implements')
    CLASS_IMPLEMENTS_NAMED      = State('Class Implements Named')
    CLASS_IMPLEMENTS_AFTER      = State('Class Implements After')
    TYPED_BEGIN                 = State('Typed')
    TYPED_NAMED                 = State('Typed Named')
    ATTR_INITIALIZE             = State('Attr Initialize')
    METHOD_SIGNATURE            = State('Method Signature')
    METHOD_ARG_TYPED            = State('Method Arg Typed')
    METHOD_ARG_NAMED            = State('Method Arg Named')
    METHOD_ARG_AFTER            = State('Method Arg After')
    METHOD_DECLARED             = State('Method Declared')
    METHOD_IMPLEMENTATION       = State('Method Implementation')
