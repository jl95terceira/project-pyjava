_RESERVED_WORDS_SET:set[str] = set()

def _reserved(word:str):

    if not word: raise Exception('empty reserved word?')
    _RESERVED_WORDS_SET.add(word)
    return word

def is_reserved(word:str):

    return word in _RESERVED_WORDS_SET

IMPORT          = _reserved('import')
STATIC          = _reserved('static')
PACKAGE         = _reserved('package')
PUBLIC          = _reserved('public')
PROTECTED       = _reserved('protected')
PRIVATE         = _reserved('private')
CLASS           = _reserved('class')
INTERFACE       = _reserved('interface')
ENUM            = _reserved('enum')
EXTENDS         = _reserved('extends')
IMPLEMENTS      = _reserved('implements')
ABSTRACT        = _reserved('abstract')
FINAL           = _reserved('final')
THROWS          = _reserved('throws')
SYNCHRONIZED    = _reserved('synchronized')
DOT             = _reserved('.')
ASTERISK        = _reserved('*')
COMMA           = _reserved(',')
SEMICOLON       = _reserved(';')
EQUALSIGN       = _reserved('=')
ATSIGN          = _reserved('@')
CURLY_OPEN      = _reserved('{')
CURLY_CLOSE     = _reserved('}')
PARENTH_OPEN    = _reserved('(')
PARENTH_CLOSE   = _reserved(')')
SQUARE_OPEN     = _reserved('[')
SQUARE_CLOSED   = _reserved(']')
ANGLE_OPEN      = _reserved('<')
ANGLE_CLOSE     = _reserved('>')
