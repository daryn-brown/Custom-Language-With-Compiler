import ply.yacc as yacc
from lexer import tokens  # Import tokens from your lexer file

# Define a simple data structure to store booking information
class BookingSystem:
    def __init__(self):
        self.events = {
            "concert": {"date": "2025-04-15", "price": 75, "available": 200},
            "theater": {"date": "2025-03-25", "price": 50, "available": 150},
            "sports": {"date": "2025-05-10", "price": 100, "available": 500}
        }
        self.bookings = {}
        self.booking_id = 1000
    
    def list_events(self, location=None):
        result = []
        for name, details in self.events.items():
            if location is None or location.lower() in name.lower():
                result.append(f"{name}: {details['date']} - ${details['price']} ({details['available']} available)")
        return result if result else ["No events found."]
    
    def book_event(self, event_name, date=None, num_tickets=1):
        event = self.find_event(event_name)
        if not event:
            return f"Event '{event_name}' not found."
        
        if date and date != self.events[event]["date"]:
            return f"Event '{event_name}' is not available on {date}."
        
        if num_tickets > self.events[event]["available"]:
            return f"Not enough tickets available for '{event_name}'."
        
        # Create temporary booking
        booking_id = self.booking_id
        self.bookings[booking_id] = {
            "event": event,
            "tickets": num_tickets,
            "date": self.events[event]["date"],
            "status": "pending",
            "total": num_tickets * self.events[event]["price"]
        }
        self.booking_id += 1
        
        return f"Booking #{booking_id} created for {num_tickets} ticket(s) to {event} on {self.events[event]['date']}. Total: ${self.bookings[booking_id]['total']}. Use CONFIRM BOOKING {booking_id} to complete."
    
    def find_event(self, event_name):
        for name in self.events:
            if event_name.lower() in name.lower():
                return name
        return None
    
    def confirm_booking(self, booking_id):
        if booking_id not in self.bookings:
            return f"Booking #{booking_id} not found."
        
        if self.bookings[booking_id]["status"] != "pending":
            return f"Booking #{booking_id} is already {self.bookings[booking_id]['status']}."
        
        event = self.bookings[booking_id]["event"]
        tickets = self.bookings[booking_id]["tickets"]
        
        # Update available tickets
        self.events[event]["available"] -= tickets
        self.bookings[booking_id]["status"] = "confirmed"
        
        return f"Booking #{booking_id} confirmed for {event} on {self.bookings[booking_id]['date']}."
    
    def pay_booking(self, booking_id, payment_method=None):
        if booking_id not in self.bookings:
            return f"Booking #{booking_id} not found."
        
        if self.bookings[booking_id]["status"] != "confirmed":
            return f"Booking #{booking_id} must be confirmed before payment."
        
        payment_info = f" with {payment_method}" if payment_method else ""
        self.bookings[booking_id]["status"] = "paid"
        
        return f"Payment successful for booking #{booking_id}{payment_info}. Total paid: ${self.bookings[booking_id]['total']}."
    
    def cancel_booking(self, booking_id):
        if booking_id not in self.bookings:
            return f"Booking #{booking_id} not found."
        
        if self.bookings[booking_id]["status"] == "cancelled":
            return f"Booking #{booking_id} is already cancelled."
        
        # Restore tickets if booking was confirmed or paid
        if self.bookings[booking_id]["status"] in ["confirmed", "paid"]:
            event = self.bookings[booking_id]["event"]
            tickets = self.bookings[booking_id]["tickets"]
            self.events[event]["available"] += tickets
        
        self.bookings[booking_id]["status"] = "cancelled"
        return f"Booking #{booking_id} has been cancelled."
    
    def update_booking(self, booking_id, new_tickets=None):
        if booking_id not in self.bookings:
            return f"Booking #{booking_id} not found."
        
        if self.bookings[booking_id]["status"] not in ["pending", "confirmed"]:
            return f"Cannot update booking #{booking_id} with status '{self.bookings[booking_id]['status']}'."
        
        if new_tickets:
            event = self.bookings[booking_id]["event"]
            old_tickets = self.bookings[booking_id]["tickets"]
            difference = new_tickets - old_tickets
            
            # Check if enough tickets are available for the update
            if difference > 0 and difference > self.events[event]["available"]:
                return f"Not enough additional tickets available for '{event}'."
            
            # Update available tickets count
            if self.bookings[booking_id]["status"] == "confirmed":
                self.events[event]["available"] -= difference
            
            # Update booking
            self.bookings[booking_id]["tickets"] = new_tickets
            self.bookings[booking_id]["total"] = new_tickets * self.events[event]["price"]
            
            return f"Booking #{booking_id} updated to {new_tickets} ticket(s). New total: ${self.bookings[booking_id]['total']}."

# Initialize the booking system
booking_system = BookingSystem()

# Grammar rules
def p_command(p):
    '''command : list_command
               | book_command
               | confirm_command
               | pay_command
               | cancel_command
               | update_command'''
    p[0] = p[1]

def p_list_command(p):
    '''list_command : LIST EVENTS
                    | LIST EVENTS IN STRING'''
    if len(p) == 3:
        p[0] = booking_system.list_events()
    else:
        p[0] = booking_system.list_events(p[4])

def p_book_command(p):
    '''book_command : BOOK STRING
                    | BOOK STRING ON DATE
                    | BOOK STRING FOR NUMBER TICKETS
                    | BOOK STRING ON DATE FOR NUMBER TICKETS'''
    if len(p) == 3:
        p[0] = booking_system.book_event(p[2])
    elif len(p) == 5 and p[3] == 'ON':
        p[0] = booking_system.book_event(p[2], date=p[4])
    elif len(p) == 5 and p[3] == 'FOR':
        p[0] = booking_system.book_event(p[2], num_tickets=int(p[4]))
    else:  # len(p) == 7
        p[0] = booking_system.book_event(p[2], date=p[4], num_tickets=int(p[6]))

def p_confirm_command(p):
    '''confirm_command : CONFIRM BOOKING NUMBER'''
    p[0] = booking_system.confirm_booking(int(p[3]))

def p_pay_command(p):
    '''pay_command : PAY BOOKING NUMBER
                   | PAY BOOKING NUMBER WITH STRING'''
    if len(p) == 4:
        p[0] = booking_system.pay_booking(int(p[3]))
    else:
        p[0] = booking_system.pay_booking(int(p[3]), payment_method=p[5])

def p_cancel_command(p):
    '''cancel_command : CANCEL BOOKING NUMBER'''
    p[0] = booking_system.cancel_booking(int(p[3]))

def p_update_command(p):
    '''update_command : UPDATE BOOKING NUMBER WITH NEW TICKETS NUMBER'''
    p[0] = booking_system.update_booking(int(p[3]), new_tickets=int(p[7]))

def p_error(p):
    if p:
        return f"Syntax error at '{p.value}'"
    else:
        return "Syntax error: unexpected end of input"

# Build the parser
parser = yacc.yacc()

def parse(input_text):
    return parser.parse(input_text)

# Example usage
def run_example():
    examples = [
        "LIST EVENTS",
        "LIST EVENTS IN theater",
        "BOOK concert",
        "BOOK theater FOR 2 TICKETS",
        "BOOK sports ON 2025-05-10 FOR 3 TICKETS",
        "CONFIRM BOOKING 1000",
        "PAY BOOKING 1000 WITH credit card",
        "UPDATE BOOKING 1000 WITH NEW TICKETS 5",
        "CANCEL BOOKING 1000"
    ]
    
    print("Example commands:")
    for example in examples:
        print(f"\nCommand: {example}")
        result = parse(example)
        print(f"Result: {result}")

if __name__ == "__main__":
    run_example()
