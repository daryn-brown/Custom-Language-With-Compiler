# Group Members: 
# Justin Alder 2007273
# Daryn Brown 2002414
# Marvis Haughton 1802529
# Peta Gaye Mundle 1403906 
# Cassandra Powell 2005742


import ply.lex as lex

# Group Members: 
# Justin Alder 2007273
# Daryn Brown 2002414
# Marvis Haughton 1802529
# Peta Gaye Mundle 1403906 
# Cassandra Powell 2005742

# Reserved Words
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
    'PRICE': 'PRICE',
    'HELP': 'HELP'
}

# Tokens
tokens = [
    'NUMBER', 'STRING', 'DATE', 'WORD'
] + list(reserved.values())

# Token Patterns
def t_STRING(t):
    r'["""][^"""]+["""]|"[^"]*"'  # Match both types of quotes
    # Remove quotes - handles both regular quotes and fancy quotes
    if t.value.startswith('"') and t.value.endswith('"'):
        t.value = t.value[1:-1]
    else:
        t.value = t.value.strip('"""')
    return t

def t_DATE(t):
    r'\d{4}-\d{2}-\d{2}'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_WORD(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    upper = t.value.upper()
    if upper in reserved:
        t.type = reserved[upper]
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t\r\n'

# Error handling rule
def t_error(t):
    print(f"Invalid character '{t.value[0]}' in command. Please check the command syntax.")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()
