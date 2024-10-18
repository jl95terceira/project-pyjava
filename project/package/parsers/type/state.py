from ... import util

class State(util.Named): pass
class States:

    BEGIN             = State('Begin')
    AFTER_NAME        = State('After Name')
    ARRAY_OPEN        = State('Array (\'[\')')
    ARRAY_CLOSE       = State('Array (\']\')')
    END               = State('End')
