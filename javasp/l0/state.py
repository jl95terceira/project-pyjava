from ..batteries import *

from .. import util

class State(util.Named): pass
class States:

    _e:Enumerator[State] = Enumerator()
    DEFAULT                 = _e(State(''))
    IN_STRING               = _e(State('In String'))
    IN_COMMENT_MULTILINE    = _e(State('In Comment (Multi-Line)'))
    IN_COMMENT_ONELINE      = _e(State('In Comment (One-Line)'))
    @staticmethod
    def values(): yield from States._e
