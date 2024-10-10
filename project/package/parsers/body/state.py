from ... import util

class State(util.Named): pass
class States:

    BEGIN   = State('Begin')
    DEFAULT = State('')
    END    = State('Stop')
