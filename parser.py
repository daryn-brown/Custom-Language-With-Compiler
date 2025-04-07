# Group Members: 
# Justin Alder 2007273
# Daryn Brown 2002414
# Marvis Haughton 1802529
# Peta Gaye Mundle 1403906 
# Cassandra Powell 2005742

import os, random
import ply.yacc as yacc
from dotenv import load_dotenv
from lexer import tokens  # Import token definitions from lexer.py
from azure.cosmos import CosmosClient, PartitionKey
import uuid

load_dotenv()

COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = os.getenv("COSMOS_DATABASE")
CONTAINER_NAME = os.getenv("COSMOS_CONTAINER")

# Verify environment variables
if not all([COSMOS_ENDPOINT, COSMOS_KEY, DATABASE_NAME, CONTAINER_NAME]):
    print("[ERROR] Missing required environment variables. Please check your .env file.")
    print("Required variables: COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_CONTAINER")
    exit(1)

try:
    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.get_database_client(DATABASE_NAME)
    container = database.get_container_client(CONTAINER_NAME)
    
    # Verify connection by trying to read container properties
    container_props = container.read()
    print("[SUCCESS] Successfully connected to Cosmos DB")
    
    # Add some test events if the container is empty
    query = "SELECT VALUE COUNT(1) FROM c"
    count = list(container.query_items(query=query, enable_cross_partition_query=True))[0]
    if count == 0:
        print("[INFO] Adding test events to the database...")
        test_events = [
            {
                "id": str(uuid.uuid4()),
                "type": "event",
                "title": "Mello Vibes",
                "venue": "Sabina Park",
                "location": "Kingston",
                "startDate": "2024-12-31",
                "endDate": "2024-12-31",
                "priceMin": 50.0,
                "priceMax": 100.0,
                "available_tickets": 100
            },
            {
                "id": str(uuid.uuid4()),
                "type": "event",
                "title": "Kingston to Montego Bay",
                "venue": "Bus Terminal",
                "location": "Kingston",
                "startDate": "2024-12-31",
                "endDate": "2024-12-31",
                "priceMin": 20.0,
                "priceMax": 40.0,
                "available_tickets": 50
            },
            {
                "id": str(uuid.uuid4()),
                "type": "event",
                "title": "Reggae Sumfest",
                "venue": "Catherine Hall",
                "location": "Montego Bay",
                "startDate": "2024-07-15",
                "endDate": "2024-07-20",
                "priceMin": 80.0,
                "priceMax": 150.0,
                "available_tickets": 200
            },
            {
                "id": str(uuid.uuid4()),
                "type": "event",
                "title": "Kingston to Port Antonio",
                "venue": "Bus Terminal",
                "location": "Kingston",
                "startDate": "2024-12-31",
                "endDate": "2024-12-31",
                "priceMin": 30.0,
                "priceMax": 50.0,
                "available_tickets": 40
            }
        ]
        for event in test_events:
            container.upsert_item(event)
        print("[SUCCESS] Added test events successfully")
        
except Exception as e:
    print(f"[ERROR] Failed to connect to Cosmos DB: {e}")
    exit(1)

# Parsing Rules
def generate_booking_code():
    return f"QTX-{random.randint(1000, 9999)}"

def p_command(p):
    '''command : list_events
               | book_event
               | confirm_booking
               | pay_booking
               | cancel_booking
               | update_event
               | add_event
               | help_command
               | word_command'''
    p[0] = p[1]

def p_help_command(p):
    '''help_command : HELP'''
    p[0] = "\n📋 Available Commands:\n" \
           "📋 LIST EVENTS - Show all available events\n" \
           "📍 LIST EVENTS IN [location] - Show events in a specific location\n" \
           "🎟️ BOOK [event_id] [quantity] - Book tickets for an event\n" \
           "✅ CONFIRM [booking_code] - Confirm a booking\n" \
           "💳 PAY [booking_code] [amount] - Make a payment\n" \
           "❌ CANCEL [booking_code] - Cancel a booking\n" \
           "🔄 UPDATE [booking_code] [new_quantity] - Update booking quantity\n" \
           "➕ ADD EVENT [title] [venue] [location] [start_date] [end_date] [price_min] [price_max] [available_tickets] - Add a new event" 
               

def p_list_events(p):
    '''list_events : LIST EVENTS IN STRING
                  | LIST EVENTS'''
    try:
        if len(p) == 5:  # LIST EVENTS IN STRING
            location = p[4].strip('"')
            query = f"SELECT * FROM c WHERE c.location = '{location}' AND c.type != 'booking'"
            events = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            if not events:
                p[0] = f"No events found in {location}"
                return
                
            result = f"\nEvents in {location}:\n"
        else:  # LIST EVENTS
            query = "SELECT * FROM c WHERE c.type != 'booking'"
            events = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            if not events:
                p[0] = "No events found"
                return
                
            result = "\nAll Available Events:\n"
            
        for event in events:
            result += f"\nEvent ID: {event.get('id', 'N/A')}"
            result += f"\nTitle: {event.get('title', 'N/A')}"
            result += f"\nType: {event.get('type', 'N/A')}"
            result += f"\nVenue: {event.get('venue', 'N/A')}"
            result += f"\nLocation: {event.get('location', 'N/A')}"
            result += f"\nDate: {event.get('startDate', 'N/A')}"
            result += f"\nPrice Range: ${event.get('priceMin', 0)} - ${event.get('priceMax', 0)}"
            result += f"\nAvailable Tickets: {event.get('available_tickets', 0)}"
            result += "\n" + "-"*50 + "\n"
            
        p[0] = result
        
    except Exception as e:
        p[0] = f"Error listing events: {str(e)}"

def p_book_event(p):
    '''book_event : BOOK STRING NUMBER
                 | BOOK STRING ON DATE FOR STRING'''
    try:
        if len(p) == 4:  # BOOK STRING NUMBER format
            event_id = p[2].strip('"')
            quantity = int(p[3])
            
            # Get the event
            event = container.read_item(event_id, partition_key=event_id)
            
            if event['available_tickets'] < quantity:
                p[0] = f"Error: Only {event['available_tickets']} tickets available"
                return
                
            # Create booking
            booking_id = str(uuid.uuid4())
            booking_code = generate_booking_code()
            
            booking = {
                "id": booking_id,
                "code": booking_code,
                "type": "booking",
                "event_id": event_id,
                "quantity": quantity,
                "status": "pending"
            }
            
            container.upsert_item(booking)
            p[0] = f"Booking created! Code: {booking_code}"
            
        else:  # BOOK STRING ON DATE FOR STRING format
            title = p[2].strip('"')
            date = p[4]  # This is already a DATE token, no need to strip quotes
            user = p[6].strip('"')
            
            # Modified query to be more inclusive - not filtering by type
            query = f"SELECT * FROM c WHERE c.title = '{title}' AND c.startDate = '{date}'"
            events = list(container.query_items(query=query, enable_cross_partition_query=True))
            
            # If no results, try a more flexible search
            if not events:
                # Try finding by title only
                title_query = f"SELECT * FROM c WHERE c.title = '{title}'"
                title_events = list(container.query_items(query=title_query, enable_cross_partition_query=True))
                
                # If still no results, try a more flexible title search
                if not title_events:
                    flexible_query = f"SELECT * FROM c WHERE CONTAINS(c.title, '{title}')"
                    flexible_events = list(container.query_items(query=flexible_query, enable_cross_partition_query=True))
                    
                    if flexible_events:
                        p[0] = f"No exact match for '{title}' on {date}. Similar events found:\n" + "\n".join([f"- {e.get('title')} on {e.get('startDate')}" for e in flexible_events])
                    else:
                        p[0] = f"No event found with title '{title}'"
                    return
                else:
                    available_dates = [e.get('startDate', 'unknown date') for e in title_events]
                    p[0] = f"Event '{title}' exists but not on {date}. Available dates: {', '.join(available_dates)}"
                    return
                
            event = events[0]
            
            if event.get('available_tickets', 0) <= 0:
                p[0] = "No tickets available"
                return
                
            # Create booking
            booking_id = str(uuid.uuid4())
            booking_code = generate_booking_code()
            
            booking = {
                "id": booking_id,
                "code": booking_code,
                "type": "booking",
                "event_id": event['id'],
                "user": user,
                "date": date,
                "quantity": 1,
                "status": "pending"
            }
            
            container.upsert_item(booking)
            p[0] = f"Booking created! Code: {booking_code}"
            
    except Exception as e:
        p[0] = f"Error creating booking: {str(e)}"

def p_confirm_booking(p):
    '''confirm_booking : CONFIRM STRING
                       | CONFIRM BOOKING STRING'''
    try:
        booking_code = p[2] if len(p) == 3 else p[3]
        booking_code = booking_code.strip('"')
        
        query = f"SELECT * FROM c WHERE c.code = '{booking_code}' AND c.type = 'booking'"
        bookings = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not bookings:
            p[0] = "Booking not found"
            return
            
        booking = bookings[0]
        if booking['status'] != 'pending':
            p[0] = f"Booking is already {booking['status']}"
            return
            
        booking['status'] = 'confirmed'
        container.replace_item(booking['id'], booking)
        p[0] = f"Booking {booking_code} confirmed successfully"
        
    except Exception as e:
        p[0] = f"Error confirming booking: {str(e)}"

def p_pay_booking(p):
    '''pay_booking : PAY STRING NUMBER
                  | PAY FOR BOOKING STRING NUMBER'''
    try:
        if len(p) == 4:  # PAY STRING NUMBER format
            booking_code = p[2].strip('"')
            amount = float(p[3])
        else:  # PAY FOR BOOKING STRING NUMBER format
            booking_code = p[4].strip('"')
            amount = float(p[5])
        
        query = f"SELECT * FROM c WHERE c.code = '{booking_code}' AND c.type = 'booking'"
        bookings = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not bookings:
            p[0] = "Booking not found"
            return
            
        booking = bookings[0]
        if booking['status'] != 'confirmed':
            p[0] = f"Cannot pay for booking in {booking['status']} status"
            return
            
        # Get event to check price
        event = container.read_item(booking['event_id'], partition_key=booking['event_id'])
        total_price = event['priceMin'] * booking['quantity']
        
        if amount < total_price:
            p[0] = f"Amount ${amount} is less than required ${total_price}"
            return
            
        booking['status'] = 'paid'
        container.replace_item(booking['id'], booking)
        p[0] = f"Payment of ${amount} processed for booking {booking_code}"
        
    except Exception as e:
        p[0] = f"Error processing payment: {str(e)}"

def p_cancel_booking(p):
    '''cancel_booking : CANCEL STRING
                     | CANCEL BOOKING STRING'''
    try:
        booking_code = p[2] if len(p) == 3 else p[3]
        booking_code = booking_code.strip('"')
        
        query = f"SELECT * FROM c WHERE c.code = '{booking_code}' AND c.type = 'booking'"
        bookings = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not bookings:
            p[0] = "Booking not found"
            return
            
        booking = bookings[0]
        if booking['status'] == 'cancelled':
            p[0] = "Booking is already cancelled"
            return
            
        # Get event to restore tickets
        event = container.read_item(booking['event_id'], partition_key=booking['event_id'])
        event['available_tickets'] += booking['quantity']
        container.replace_item(event['id'], event)
        
        booking['status'] = 'cancelled'
        container.replace_item(booking['id'], booking)
        p[0] = f"Booking {booking_code} cancelled successfully"
        
    except Exception as e:
        p[0] = f"Error cancelling booking: {str(e)}"

def p_update_event(p):
    '''update_event : UPDATE STRING NUMBER
                   | UPDATE EVENT STRING WITH NUMBER NEW TICKETS'''
    try:
        if len(p) == 4:  # UPDATE STRING NUMBER format
            event_id = p[2].strip('"')
            new_tickets = int(p[3])
        else:  # UPDATE EVENT STRING WITH NUMBER NEW TICKETS format
            event_id = p[3].strip('"')
            new_tickets = int(p[5])
        
        event = container.read_item(event_id, partition_key=event_id)
        event['available_tickets'] = new_tickets
        container.replace_item(event['id'], event)
        
        p[0] = f"Event {event_id} updated with {new_tickets} available tickets"
        
    except Exception as e:
        p[0] = f"Error updating event: {str(e)}"

def p_add_event(p):
    '''add_event : ADD EVENT STRING STRING STRING DATE DATE NUMBER NUMBER NUMBER
                | ADD EVENT STRING AT STRING IN STRING FROM DATE TO DATE PRICE NUMBER TO NUMBER'''
    try:
        if len(p) == 11:  # Original format
            title = p[3].strip('"')
            venue = p[4].strip('"')
            location = p[5].strip('"')
            start_date = p[6]
            end_date = p[7]
            price_min = float(p[8])
            price_max = float(p[9])
            available_tickets = int(p[10])
        else:  # New format with AT, IN, FROM, TO, PRICE
            title = p[3].strip('"')
            venue = p[5].strip('"')
            location = p[7].strip('"')
            start_date = p[9]
            end_date = p[11]
            price_min = float(p[13])
            price_max = float(p[15])
            available_tickets = 100  # Default for new format
        
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "type": "event",
            "title": title,
            "venue": venue,
            "location": location,
            "startDate": start_date,
            "endDate": end_date,
            "priceMin": price_min,
            "priceMax": price_max,
            "available_tickets": available_tickets
        }
        
        container.upsert_item(event)
        p[0] = f"Event {title} added successfully with ID: {event_id}"
        
    except Exception as e:
        p[0] = f"Error adding event: {str(e)}"

# Add a new rule that explicitly uses the WORD token
def p_word_command(p):
    '''word_command : WORD'''
    p[0] = f"Unrecognized command: {p[1]}. Type 'help' for available commands."

# Improved error handling
def p_error(p):
    if p:
        error_msg = f"Syntax error: unexpected '{p.value}'"
        print(error_msg)
        return error_msg
    else:
        error_msg = "Syntax error: unexpected end of command"
        print(error_msg)
        return error_msg

parser = yacc.yacc(debug=False, write_tables=False, errorlog=yacc.NullLogger()) 