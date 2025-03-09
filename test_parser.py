from parser import parser, bookings

def test_parser(input_text):
    print(f"\nTesting: {input_text}")
    try:
        parser.parse(input_text)
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 40)  # Separator for readability

# Perform a booking first and store its ID
test_parser('BOOK "Coldplay Concert" ON 2021-12-01 FOR "Alice"')

# Get the actual booking ID
actual_booking_id = next(iter(bookings.keys()))  # Get the first key in bookings

# Test Cases (Executing in the correct order)
test_cases = [
    f"CONFIRM BOOKING {actual_booking_id}",  # Confirm first
    f"PAY FOR BOOKING {actual_booking_id}",  # Then pay
    f"CANCEL BOOKING {actual_booking_id}",  # Cancel only after confirming & paying
    'UPDATE EVENT "Coldplay Concert" WITH 10 NEW TICKETS'
]

# Run all test cases
for case in test_cases:
    test_parser(case)
