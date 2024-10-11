from ... import util

class State(util.Named): pass
class States:

    BEGIN             = State('Begin')
    DEFAULT           = State('')
    DEFAULT_2         = State('2')
    END               = State('End')
