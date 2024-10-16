from ... import util

class State(util.Named): pass
class States:

    BEGIN         = State('Begin')
    AFTER_PACKAGE = State('After Package')
    AFTER_NAME    = State('After Name')
    END           = State('End')
