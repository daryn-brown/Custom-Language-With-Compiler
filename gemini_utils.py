import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables and configure Gemini
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")

# Pre-defined command templates for efficiency
COMMAND_TEMPLATES = {
    "LIST": [
        'LIST EVENTS IN "Location"',
        'LIST EVENTS'
    ],
    "BOOK": [
        'BOOK "Event Name" ON 2024-12-31 FOR "Person Name"',
        'BOOK "Event ID" 2'
    ],
    "CONFIRM": [
        'CONFIRM "QTX-1234"',
        'CONFIRM BOOKING "QTX-1234"'
    ],
    "PAY": [
        'PAY "QTX-1234" 100',
        'PAY FOR BOOKING "QTX-1234" 100'
    ],
    "CANCEL": [
        'CANCEL "QTX-1234"'
    ],
    "UPDATE": [
        'UPDATE "Event ID" 50',
        'UPDATE EVENT "Event Name" WITH 10 NEW TICKETS'
    ],
    "ADD": [
        'ADD EVENT "Title" "Venue" "Location" 2024-12-31 2024-12-31 50 100 100',
        'ADD EVENT "Title" AT "Venue" IN "Location" FROM 2024-12-31 TO 2024-12-31 PRICE 50 TO 100'
    ]
}

def suggest_next_command(user_input: str) -> str:
    """
    Get a command suggestion from Gemini based on the user's partial input.
    """
    # Extract the command type from user input
    command_type = user_input.split()[0].upper() if user_input else ""
    
    # If we have a matching template, use it to guide the suggestion
    templates = COMMAND_TEMPLATES.get(command_type, [])
    template_str = "\n".join(f"- {t}" for t in templates)
    
    prompt = f"""
You are a CLI command suggestion assistant for a Ticket Booking system.
The user typed: '{user_input}'

Available command format{'s' if len(templates) > 1 else ''}:
{template_str}

Rules:
1. Use exact date format: YYYY-MM-DD
2. Use quotes around names/locations
3. Maintain proper spacing between components
4. Return only the completed command

Based on the user's input, suggest the most likely complete command.
Only return the command, no additional text.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip().strip("`")
    except Exception as e:
        return f"⚠️ Gemini Error: {e}" 