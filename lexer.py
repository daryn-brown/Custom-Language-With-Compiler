import ply.lex as lex

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
    'TICKETS': 'TICKETS'
}

# Token Definitions
tokens = [
    'NUMBER', 'STRING', 'DATE'
] + list(reserved.values())  # Include reserved words in tokens

# Token Patterns
t_NUMBER = r'\d+'

# Date format (YYYY-MM-DD)
def t_DATE(t):
    r'\d{4}-\d{2}-\d{2}'
    return t

# Ensure reserved words are correctly recognized
def t_STRING(t):
    r'"[^"]*"|\b[a-zA-Z][a-zA-Z0-9_]*\b'  # Match quoted text OR single words
    t.type = reserved.get(t.value.upper(), 'STRING')  # Check if it's a reserved word
    t.value = t.value.strip('"')  # Remove quotes if present
    return t

t_ignore = ' \t\n'

# Error Handling
def t_error(t):
    print(f"Illegal character {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()
