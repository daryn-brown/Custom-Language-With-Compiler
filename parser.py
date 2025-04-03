import os
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

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


# Database Simulation
bookings = {}  # {booking_id: (event_name, user_name, status)}
events = { "Coldplay Concert": 50 }  # {event_name: available_tickets}
booking_id_counter = 1000

# Parsing Rules

def p_add_event(p):
    'command : ADD WORD STRING AT STRING IN STRING FROM DATE TO DATE PRICE NUMBER TO NUMBER'
    item_type = p[2].lower() + " ticket"  # e.g., "concert ticket", "bus ticket"
    title = p[3]
    venue = p[5]
    location = p[7]
    start = p[9]
    end = p[11]
    price_min = float(p[13])
    price_max = float(p[15])

    event_id = str(uuid.uuid4())

    event_data = {
        "id": event_id,
        "type": item_type,
        "title": title,
        "venue": venue,
        "location": location,
        "startDate": start,
        "endDate": end,
        "priceMin": price_min,
        "priceMax": price_max,
        "available_tickets": 100
    }

    try:
        container.upsert_item(event_data)
        print(f"✅ Added '{title}' ({item_type}) with ID: {event_id}")
    except Exception as e:
        print(f"❌ Failed to insert: {e}")

def p_list_events(p):
    'command : LIST EVENTS IN STRING'
    location = p[4].strip('"')
    print(f"📍 Events in {location}:")
    try:
        query = f"SELECT * FROM c WHERE LOWER(c.location) = '{location.lower()}'"
        for item in container.query_items(query=query, enable_cross_partition_query=True):
            print(f"- {item['title']} ({item.get('type', 'ticket')}) at {item['venue']} from {item['startDate']} to {item['endDate']}, "
                  f"${item['priceMin']} - ${item['priceMax']} ({item['available_tickets']} tickets left)")
    except Exception as e:
        print(f"❌ Failed to fetch events: {e}")


def p_book_event(p):
    'command : BOOK STRING ON DATE FOR STRING'
    global booking_id_counter
    title = p[2].strip('"')
    date = p[4]
    user = p[6].strip('"')

    try:
        query = f"SELECT * FROM c WHERE c.title = '{title}'"
        results = list(container.query_items(query=query, enable_cross_partition_query=True))
        if not results:
            print("❌ Event not found.")
            return
        event = results[0]

        if event['available_tickets'] <= 0:
            print("❌ No tickets available.")
            return

        # Decrease ticket count
        event['available_tickets'] -= 1
        container.replace_item(event['id'], event)

        # Store booking
        bookings[booking_id_counter] = (event['id'], user, date, "booked")
        print(f"✅ Booking confirmed! ID: #{booking_id_counter}")
        booking_id_counter += 1

    except Exception as e:
        print(f"❌ Booking error: {e}")

def p_confirm_booking(p):
    'command : CONFIRM BOOKING NUMBER'
    booking_id = int(p[3])
    if booking_id in bookings:
        data = bookings[booking_id]
        bookings[booking_id] = (data[0], data[1], data[2], "confirmed")
        print(f"✅ Booking #{booking_id} confirmed.")
    else:
        print("❌ Booking ID not found.")

def p_pay_booking(p):
    'command : PAY FOR BOOKING NUMBER'
    booking_id = int(p[4])
    if booking_id in bookings and bookings[booking_id][3] == "confirmed":
        data = bookings[booking_id]
        bookings[booking_id] = (data[0], data[1], data[2], "paid")
        print(f"💳 Payment completed for booking #{booking_id}")
    else:
        print("❌ Booking not confirmed or not found.")

def p_cancel_booking(p):
    'command : CANCEL BOOKING NUMBER'
    booking_id = int(p[3])
    if booking_id in bookings:
        event_id, _, _, _ = bookings[booking_id]
        try:
            event = container.read_item(event_id, partition_key=event_id)
            event['available_tickets'] += 1
            container.replace_item(event_id, event)
            del bookings[booking_id]
            print(f"❌ Booking #{booking_id} canceled and ticket restored.")
        except Exception as e:
            print(f"❌ Error canceling booking: {e}")
    else:
        print("❌ Booking not found.")

def p_update_event(p):
    'command : UPDATE EVENT STRING WITH NUMBER NEW TICKETS'
    title = p[3].strip('"')
    new_tickets = int(p[5])

    try:
        query = f"SELECT * FROM c WHERE c.title = '{title}'"
        results = list(container.query_items(query=query, enable_cross_partition_query=True))
        if not results:
            print("❌ Event not found.")
            return
        event = results[0]
        event['available_tickets'] += new_tickets
        container.replace_item(event['id'], event)
        print(f"🔁 Updated '{title}' with {new_tickets} new tickets.")
    except Exception as e:
        print(f"❌ Update error: {e}")

# Improved error handling
def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}', token type: {p.type}")
    else:
        print("Syntax error at end of input.")

parser = yacc.yacc(debug=False, write_tables=False)
