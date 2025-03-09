import ply.yacc as yacc
from lexer import tokens  # Import token definitions from lexer.py

# Database Simulation
bookings = {}  # {booking_id: (event_name, user_name, status)}
events = { "Coldplay Concert": 50 }  # {event_name: available_tickets}
booking_id_counter = 1000

# Parsing Rules
def p_list_events(p):
    'command : LIST EVENTS IN STRING'
    location = p[4]
    print(f"Fetching events in {location}...")
    print(events)

def p_book_event(p):
    'command : BOOK STRING ON DATE FOR STRING'  # FIXED: Use DATE instead of STRING
    global booking_id_counter
    event = p[2].strip('"')
    date = p[4]  # Date is now a separate token
    user = p[6].strip('"')
    
    if event in events and events[event] > 0:
        booking_id = booking_id_counter
        bookings[booking_id] = (event, date, user, "booked")
        events[event] -= 1
        booking_id_counter += 1
        print(f"Booking confirmed! Reservation ID: #{booking_id}")
    else:
        print("Error: Event unavailable or sold out.")

def p_confirm_booking(p):
    'command : CONFIRM BOOKING NUMBER'
    booking_id = int(p[3])
    if booking_id in bookings:
        bookings[booking_id] = (bookings[booking_id][0], bookings[booking_id][1], bookings[booking_id][2], "confirmed")
        print(f"Booking #{booking_id} confirmed.")
    else:
        print("Error: Booking ID not found.")

def p_pay_booking(p):
    'command : PAY FOR BOOKING NUMBER'
    booking_id = int(p[4])
    if booking_id in bookings and bookings[booking_id][3] == "confirmed":
        bookings[booking_id] = (bookings[booking_id][0], bookings[booking_id][1], bookings[booking_id][2], "paid")
        print(f"Payment successful for booking #{booking_id}")
    else:
        print("Error: Booking not confirmed yet.")

def p_cancel_booking(p):
    'command : CANCEL BOOKING NUMBER'  # FIXED: p[2] is correct index for NUMBER
    booking_id = int(p[3])
    if booking_id in bookings:
        events[bookings[booking_id][0]] += 1  # Return ticket to inventory
        del bookings[booking_id]
        print(f"Booking #{booking_id} canceled.")
    else:
        print("Error: Booking ID not found.")

def p_update_event(p):
    'command : UPDATE EVENT STRING WITH NUMBER NEW TICKETS'
    event = p[3].strip('"')
    new_tickets = int(p[5])
    if event in events:
        events[event] += new_tickets
    else:
        events[event] = new_tickets
    print(f"Updated {event} with {new_tickets} new tickets.")

# Improved error handling
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', token type: {p.type}")
    else:
        print("Syntax error at end of input.")

parser = yacc.yacc(debug=True, write_tables=False)
