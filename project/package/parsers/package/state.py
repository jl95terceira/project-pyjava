from ... import util

class State(util.Named): pass
class States:

    BEGIN             = State('Begin')
    AFTER_PACKAGE           = State('')
    AFTER_NAME         = State('2')
    END               = State('End')
