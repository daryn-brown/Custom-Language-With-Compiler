# Group Members: 
# Justin Alder 2007273
# Daryn Brown 2002414
# Marvis Haughton 1802529
# Peta Gaye Mundle 1403906 
# Cassandra Powell 2005742

import sys
sys.stdout.reconfigure(encoding='utf-8')
from parser import parser



while True:
    try:
        user_input = input(">> ")
        if user_input.lower() == 'exit':
            break
        parser.parse(user_input)
    except EOFError:
        break

print("Enter your commands")