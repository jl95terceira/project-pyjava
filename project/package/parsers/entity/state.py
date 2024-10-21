from ... import util

class State(util.Named): pass
class States:

    AINTERFACE                  = State('@interface')
    AINTERFACE_NAMED            = State('@interface Named')
    ATTR_BEGIN                  = State('Attr')
    ATTR_INITIALIZE             = State('Attr Initialize')
    ATTR_MULTI_SEP              = State('Attr Multi Sep.')
    ATTR_MULTI                  = State('Attr Multi')
    CLASS                       = State('Class')
    CLASS_AFTER_NAME            = State('Class After-Name')
    CLASS_EXTENDS               = State('Class Ext.')
    CLASS_SUPERCLASS            = State('Class Super')
    CLASS_SUPERCLASS_NAMED      = State('Class Super Named')
    CONSTRUCTOR_SIGNATURE       = State('Constr. Sign.')
    CONSTRUCTOR_DECLARED        = State('Constr. Declared')
    CONSTRUCTOR_THROWS          = State('Constr. Throws')
    CONSTRUCTOR_THROWS_AFTER    = State('Constr. Throws After')
    CONSTRUCTOR_BODY            = State('Constr. Body')
    DEFAULT                     = State('')
    ENUM                        = State('Enum')
    ENUM_NAMED                  = State('Enum Named')
    ENUM_DEFINED                = State('Enum Defined')
    RECORD                      = State('Record')
    RECORD_AFTER_NAME           = State('Record After Name')
    INITIALIZER_BODY            = State('Initializer Body')
    LOOKAHEAD_1                 = State('Declaration (1)') # 1st word (type? of attribute or of method?)
    LOOKAHEAD_2                 = State('Declaration (2)') # 2nd word (name? of attribute or of method?)
    METHOD_SIGNATURE            = State('Method Signature')
    METHOD_DECLARED             = State('Method Declared')
    METHOD_THROWS               = State('Method Throws')
    METHOD_THROWS_AFTER         = State('Method Throws After')
    METHOD_BODY                 = State('Method Body')
    METHOD_DEFAULT_VALUE        = State('Method Default Value')
    METHOD_DEFAULT_VALUE_AFTER  = State('Method Default Value After')

class CallArgsState(util.Named): pass
class CallArgsStates:

    BEGIN    = CallArgsState('Begin')
    DEFAULT  = CallArgsState('')
    SEPARATE = CallArgsState('Sep.')
