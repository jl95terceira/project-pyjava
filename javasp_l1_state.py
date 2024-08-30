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
    CONSTRUCTOR_SIGNATURE       = State('Constructor Signature')
    CONSTRUCTOR_BODY            = State('Constructor Body')
    STATIC_CONSTRUCTOR_BODY     = State('Static Constructor Body')
    TYPED_BEGIN                 = State('Typed')
    TYPED_NAMED                 = State('Typed Named')
    ATTR_INITIALIZE             = State('Attr Initialize')
    METHOD_SIGNATURE            = State('Method Signature')
    METHOD_DECLARED             = State('Method Declared')
    METHOD_BODY                 = State('Method Body')

class ArgsState(util.Named): pass
class ArgsStates:

    BEGIN   = ArgsState('')
    TYPED   = ArgsState('Typed')
    NAMED   = ArgsState('Typed and Named')
    AFTER   = ArgsState('After (Separator)')
