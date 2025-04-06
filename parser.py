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

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)


# Database Simulation
bookings = {}  # {booking_id: (event_name, user_name, status)}
events = { "Coldplay Concert": 50 }  # {event_name: available_tickets}
booking_id_counter = 1000

# Parsing Rules

def generate_booking_code():
    return f"QTX-{random.randint(1000, 9999)}"

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

def p_list_all_events(p):
    'command : LIST EVENTS'
    print("📍 All Events:")
    try:
        query = "SELECT * FROM c"
        for item in container.query_items(query=query, enable_cross_partition_query=True):
            print(f"- {item['title']} ({item.get('type', 'event')}) at {item['venue']} in {item['location']} from {item['startDate']} to {item['endDate']}, "
                  f"${item['priceMin']} - ${item['priceMax']} ({item['available_tickets']} tickets left)")
    except Exception as e:
        print(f"❌ Failed to fetch events: {e}")



def p_book_event(p):
    'command : BOOK STRING ON DATE FOR STRING'
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

        event['available_tickets'] -= 1
        container.replace_item(event['id'], event)

        booking_id = str(uuid.uuid4())
        booking_code = generate_booking_code()

        booking = {
            "id": booking_id,
            "code": booking_code,
            "type": "booking",
            "event_id": event["id"],
            "user": user,
            "date": date,
            "status": "booked"
        }
        container.upsert_item(booking)
        print(f"✅ Booking logged! ID: #{booking_code}")

    except Exception as e:
        print(f"❌ Booking error: {e}")


def p_confirm_booking(p):
    'command : CONFIRM BOOKING STRING'
    code = p[3].strip('"')
    query = f"SELECT * FROM c WHERE c.code = '{code}' AND c.type = 'booking'"
    results = list(container.query_items(query=query, enable_cross_partition_query=True))
    if results:
        booking = results[0]
        booking["status"] = "confirmed"
        container.replace_item(booking["id"], booking)
        print(f"✅ Booking {code} confirmed.")
    else:
        print("❌ Booking ID not found.")

def p_pay_booking(p):
    'command : PAY FOR BOOKING STRING'
    code = p[4].strip('"')
    query = f"SELECT * FROM c WHERE c.code = '{code}' AND c.type = 'booking'"
    results = list(container.query_items(query=query, enable_cross_partition_query=True))
    if results and results[0]["status"] == "confirmed":
        booking = results[0]
        booking["status"] = "paid"
        container.replace_item(booking["id"], booking)
        print(f"💳 Payment completed for booking {code}")
    else:
        print("❌ Booking not confirmed or not found.")



def p_cancel_booking(p):
    'command : CANCEL BOOKING STRING'
    code = p[3].strip('"')
    query = f"SELECT * FROM c WHERE c.code = '{code}' AND c.type = 'booking'"
    results = list(container.query_items(query=query, enable_cross_partition_query=True))
    if results:
        booking = results[0]
        event_id = booking["event_id"]
        event = container.read_item(event_id, partition_key=event_id)
        event["available_tickets"] += 1
        container.replace_item(event_id, event)
        container.delete_item(booking["id"], partition_key=booking["id"])
        print(f"❌ Booking {code} canceled and ticket restored.")
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
