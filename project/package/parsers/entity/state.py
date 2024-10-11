from ... import util

class State(util.Named): pass
class States:

    DEFAULT                     = State('')
    CLASS_BEGIN                 = State('Class')
    CLASS_AFTER_NAME            = State('Class After-Name')
    CLASS_EXTENDS               = State('Class Ext.')
    CLASS_SUPERCLASS            = State('Class Super')
    CLASS_SUPERCLASS_NAMED      = State('Class Super Named')
    ENUM                        = State('Enum')
    ENUM_NAMED                  = State('Enum Named')
    ENUM_DEFINED                = State('Enum Defined')
    CONSTRUCTOR_SIGNATURE       = State('Constr. Sign.')
    CONSTRUCTOR_DECLARED        = State('Constr. Declared')
    CONSTRUCTOR_BODY            = State('Constr. Body')
    STATIC_CONSTRUCTOR_BODY     = State('Static Constr. Body')
    ATTR_BEGIN                  = State('Attr')
    UNKNOWN_1                   = State('Declaration (1)') # 1st word (type? of attribute or of method?)
    UNKNOWN_2                   = State('Declaration (2)') # 2nd word (name? of attribute or of method?)
    ATTR_INITIALIZE             = State('Attr Initialize')
    METHOD_SIGNATURE            = State('Method Signature')
    METHOD_DECLARED             = State('Method Declared')
    METHOD_THROWS               = State('Method Throws')
    METHOD_THROWS_AFTER         = State('Method Throws After')
    METHOD_BODY                 = State('Method Body')

class CallArgsState(util.Named): pass
class CallArgsStates:

    BEGIN    = CallArgsState('Begin')
    DEFAULT  = CallArgsState('')
    SEPARATE = CallArgsState('Sep.')
