import dataclasses

@dataclasses.dataclass(frozen=True)
class L1State: 
    
    name:str

class L1States:

    NONE             = L1State(name='')
    PACKAGE          = L1State(name='Package')
    IMPORT           = L1State(name='Import')
    ANNOTATION       = L1State(name='Annotation')
    CLASS            = L1State(name='Class')
    CLASS_NAMED      = L1State(name='Class (Named)')
    CLASS_EXTENDS    = L1State(name='Class Extends')
    CLASS_IMPLEMENTS = L1State(name='Class Implements')