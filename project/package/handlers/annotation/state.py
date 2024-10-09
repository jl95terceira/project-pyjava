from ... import util

class State(util.Named): pass
class States:

    BEGIN   = State('Begin')
    DEFAULT = State('')
    NAMED   = State('Named')
    ARGS    = State('Args')
    END     = State('Stop')
