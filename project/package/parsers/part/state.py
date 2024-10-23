from ...          import util

class State(util.Named): pass
class States:

    DEFAULT                 = State('')
    IN_STRING               = State('In String')
    IN_COMMENT_MULTILINE    = State('In Comment (Multi-Line)')
    IN_COMMENT_ONELINE      = State('In Comment (One-Line)')
