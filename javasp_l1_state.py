import javasp_util as util

class State(util.Named): pass
class States:

    BEGIN                       = State('')
    PACKAGE                     = State('Package')
    IMPORT                      = State('Import')
    ANNOTATION                  = State('Annotation')
    CLASS_BEGIN                 = State('Class')
    CLASS_AFTER_NAME            = State('Class After-Name')
    CLASS_EXTENDS               = State('Class Ext.')
    CLASS_IMPLEMENTS            = State('Class Impl.')
    CLASS_IMPLEMENTS_NAMED      = State('Class Impl. Named')
    CLASS_IMPLEMENTS_AFTER      = State('Class Impl. After')
    ENUM                        = State('Enum')
    ENUM_NAMED                  = State('Enum Named')
    CONSTRUCTOR_SIGNATURE       = State('Constr. Sign.')
    CONSTRUCTOR_DECLARED        = State('Constr. Declared')
    CONSTRUCTOR_BODY            = State('Constr. Body')
    STATIC_CONSTRUCTOR_BODY     = State('Static Constr. Body')
    ATTR_BEGIN                  = State('Attr')
    ATTR_TYPED                  = State('Attr Typed')
    ATTR_NAMED                  = State('Attr Named')
    ATTR_INITIALIZE             = State('Attr Initialize')
    METHOD_SIGNATURE            = State('Method Signature')
    METHOD_DECLARED             = State('Method Declared')
    METHOD_BODY                 = State('Method Body')

class TypeState(util.Named): pass
class TypeStates:

    BEGIN       = TypeState('')
    ONGOING     = TypeState('Ongoing')
    ONGOING_DOT = TypeState('Ongoing: Dot')

class SignState(util.Named): pass
class SignStates:

    BEGIN            = SignState('')
    ONGOING          = SignState('Ongoing')
    ONGOING_TYPED    = SignState('Ongoing: Typed')
    ONGOING_NAMED    = SignState('Ongoing: Named')
    ONGOING_SEPARATE = SignState('Ongoing: Sep.')

class BodyState(util.Named): pass
class BodyStates:

    BEGIN   = BodyState('')
    ONGOING = BodyState('Ongoing')

class ParArgsState(util.Named): pass
class ParArgsStates:

    BEGIN         = ParArgsState('')
    ONGOING       = ParArgsState('Ongoing')
    ONGOING_SEP   = ParArgsState('Ongoing: Sep.')
