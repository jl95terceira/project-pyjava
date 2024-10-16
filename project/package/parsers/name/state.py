from ... import util

class State(util.Named): pass
class States:

    BEGIN     = State('Begin')
    DEFAULT   = State('')
    AFTER_DOT = State('.')
    END       = State('End')
