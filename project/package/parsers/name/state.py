from ... import util

class State(util.Named): pass
class States:

    BEGIN        = State('Begin')
    DEFAULT      = State('')
    AFTER_DOT    = State('.')
    ARRAY_OPEN   = State('[')
    ARRAY_CLOSE  = State(']')
    END          = State('End')
