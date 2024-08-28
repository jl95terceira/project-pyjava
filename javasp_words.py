_RESERVED_WORDS_SET:set[str] = set()

def reserved(word:str):

    if not word: raise Exception('empty reserved word?')
    _RESERVED_WORDS_SET.add(word)
    return word

def is_reserved(word:str):

    return word in _RESERVED_WORDS_SET

IMPORT          = reserved('import')
STATIC          = reserved('static')
PACKAGE         = reserved('package')
CLASS           = reserved('class')
EXTENDS         = reserved('extends')
IMPLEMENTS      = reserved('implements')
FINAL           = reserved('final')
COMMA           = reserved(',')
SEMICOLON       = reserved(';')
EQUALSIGN       = reserved('=')
ATSIGN          = reserved('@')
BRACE_OPEN      = reserved('{')
BRACE_CLOSE     = reserved('}')
PARENTH_OPEN    = reserved('(')
PARENTH_CLOSE   = reserved(')')
