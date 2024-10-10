from ... import util

class State(util.Named): pass
class States:

    BEGIN        = State('Begin')
    DEFAULT      = State('')
    ARG_TYPED    = State('Arg Typed')
    ARG_NAMED    = State('Arg Named')
    ARG_SEPARATE = State('Arg Sep.')
    END          = State('End')
