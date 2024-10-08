from ... import util

class State(util.Named): pass
class States:

    BEGIN       = State('Begin')
    DEFAULT     = State('')
    ARRAY_OPEN  = State('Array (\'[\')')
    ARRAY_CLOSE = State('Array (\']\')')
    AFTERDOT    = State('After-Dot')
    GENERICS    = State('Generics')
    END         = State('End')
