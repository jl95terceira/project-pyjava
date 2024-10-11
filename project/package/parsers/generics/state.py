from ... import util

class State(util.Named): pass
class States:

    BEGIN            = State('Begin')
    DEFAULT          = State('')
    AFTER            = State('After')
    CONSTRAINT       = State('Constraint')
    SEP              = State('Sep.')
    END              = State('End')
