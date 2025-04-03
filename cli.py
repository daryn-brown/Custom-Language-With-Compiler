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