import lib.ply.lex as lex

tokens = (
    'NUMBER',
    'LPAREN',
    'RPAREN',
    'RETURN',
    'COLON',
    'ARROW',
    'PERIOD',
    'COMMA',
    'SEMICOLON',
    'PLUS',
    'EQUALS',
    'FUNCTION',
    'STRUCTURE',
    'SNAKE_NAME',
    'CAMEL_NAME',
)


def t_STRUCTURE(t):
    r'structure'
    return t

def t_FUNCTION(t):
    r'function'
    return t

def t_RETURN(t):
    r'return'
    return t

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_COLON = r':'
t_ARROW = r'->'
t_PERIOD = r'\.'
t_COMMA = r','
t_SEMICOLON = r';'
t_PLUS = r'\+'
t_EQUALS = r'='

def t_NUMBER(t):
    r'\d+(\.\d*)?'
    t.value = float(t.value)
    return t

t_SNAKE_NAME = r'[a-z_]+'
t_CAMEL_NAME = r'([A-Z][a-z]*)+'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    raise ValueError('Illegal character', t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()
