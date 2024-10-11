from ... import util

class State(util.Named): pass
class States:

    BEGIN             = State('Begin')
    AFTER_IMPORT           = State('')
    AFTER_NAME         = State('2')
    END               = State('End')
