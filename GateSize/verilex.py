# Structural Verilog Lexer

import ply.lex as lex

reserved = {
    'module' : 'MODULE', 
    'endmodule' : 'ENDMODULE', 
    'input' : 'INPUT', 
    'output' : 'OUTPUT', 
    'wire' : 'WIRE'}

tokens = list(reserved.values()) + ['ID', 'COMMA', 'SEMI', 'COLON', 'DOT', 'EQ', 'LPAREN', 'RPAREN', 'LSQUARE', 'RSQUARE', 'LCURLY', 'RCURLY', 'INTEGER']

t_COMMA = r','
t_SEMI = r';'
t_COLON = r':'
t_DOT = r'\.'
t_EQ = r'\='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_INTEGER = r'[0-9]+'

t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t


def t_ignore_COMMENT(t):
    r'//.*\n'
    t.lexer.lineno += 1

# Define a rule to track line numbers (\n tokens otherwise discarded)
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()
