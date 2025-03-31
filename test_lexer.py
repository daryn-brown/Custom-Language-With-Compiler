from lexer import lexer

def test_lexer(input_text):
    lexer.input(input_text)
    print(f"Testing: {input_text}")
    for tok in lexer:
        print(tok)
    print("-" * 40)  # Separator for readability

# Test Cases
test_cases = [
    'LIST EVENTS IN Kingston',
    'BOOK "Coldplay Concert" ON 2021-12-01 FOR "Alice"',
    'CANCEL BOOKING 1001',
    'CONFIRM BOOKING 1002',
    'PAY FOR BOOKING 1002',
    'UPDATE EVENT "Coldplay Concert" WITH 10 NEW TICKETS'
]

# Run all test cases
for case in test_cases:
    test_lexer(case)

