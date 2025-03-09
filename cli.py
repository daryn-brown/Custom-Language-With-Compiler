from parser import parser

print("Welcome to the Ticket Booking System CLI")
print("Enter your commands or type 'exit' to quit.")

while True:
    try:
        user_input = input(">> ")
        if user_input.lower() == 'exit':
            break
        parser.parse(user_input)
    except EOFError:
        break
