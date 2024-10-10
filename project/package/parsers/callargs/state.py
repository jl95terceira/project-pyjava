from ... import util

class CallArgsState(util.Named): pass
class CallArgsStates:

    BEGIN    = CallArgsState('Begin')
    DEFAULT  = CallArgsState('')
    SEPARATE = CallArgsState('Separate')
    END      = CallArgsState('End')
