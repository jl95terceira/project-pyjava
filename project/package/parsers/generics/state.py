from ... import util

class State(util.Named): pass
class States:

    BEGIN                = State('Begin')
    DEFAULT              = State('')
    DEFAULT_2            = State('2')
    AFTER                = State('After')
    CONSTRAINT           = State('Constraint')
    CONSTRAINT_LOOKAHEAD = State('Constraint Lookahead')
    SEP                  = State('Sep.')
    END                  = State('End')
