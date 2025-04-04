import ply.lex as lex

# Reserved Words (excluding types like CONCERT, MOVIE)
reserved = {
    'LIST': 'LIST',
    'EVENTS': 'EVENTS',
    'IN': 'IN',
    'BOOK': 'BOOK',
    'ON': 'ON',
    'FOR': 'FOR',
    'CONFIRM': 'CONFIRM',
    'BOOKING': 'BOOKING',
    'PAY': 'PAY',
    'CANCEL': 'CANCEL',
    'UPDATE': 'UPDATE',
    'EVENT': 'EVENT',
    'WITH': 'WITH',
    'NEW': 'NEW',
    'TICKETS': 'TICKETS',
    'ADD': 'ADD',
    'AT': 'AT',
    'FROM': 'FROM',
    'TO': 'TO',
    'PRICE': 'PRICE'
}

# Tokens
tokens = [
    'NUMBER', 'STRING', 'DATE', 'WORD'
] + list(reserved.values())

# Token Patterns
t_NUMBER = r'\d+'

def t_DATE(t):
    r'\d{4}-\d{2}-\d{2}'
    return t

def t_STRING(t):
    r'["“”][^"“”]+["“”]'  # Only match quoted strings
    t.value = t.value.strip('"“”')
    return t


def t_WORD(t):
    r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'
    t.type = reserved.get(t.value.upper(), 'WORD')  # Reserved or generic WORD
    return t

t_ignore = ' \t\r\n'

def t_error(t):
    print(f"Illegal character {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()
