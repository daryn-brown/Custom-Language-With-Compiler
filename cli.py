import os
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from gemini_completer import GeminiCompleter
from gemini_utils import suggest_next_command
from parser import parser

load_dotenv()

# Configure the CLI
session = PromptSession(
    completer=GeminiCompleter(),
    style=Style.from_dict({
        'completion-menu.completion': 'bg:#008888 #ffffff',
        'completion-menu.completion.current': 'bg:#00aaaa #000000',
        'scrollbar.background': 'bg:#88aaaa',
        'scrollbar.button': 'bg:#222222',
    })
)

def main():
    print("🎫 Welcome to QuickTix CLI!")
    print("ℹ️ Type 'help' for available commands or start typing to see suggestions.")
    print("💡 Press TAB to see command completions.")
    
    while True:
        try:
            # Get user input with inline suggestions
            user_input = session.prompt("QuickTix> ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() == 'exit':
                print("👋 Goodbye!")
                break
                
            if user_input.lower() == 'help':
                print("\n📋 Available Commands:")
                print("📋 LIST EVENTS - Show all available events")
                print("📍 LIST EVENTS IN <location> - Show events in a specific location")
                print("🎟️ BOOK <event_id> <quantity> - Book tickets for an event")
                print("✅ CONFIRM <booking_code> - Confirm a booking")
                print("💳 PAY <booking_code> <amount> - Make a payment")
                print("❌ CANCEL <booking_code> - Cancel a booking")
                print("🔄 UPDATE <booking_code> <new_quantity> - Update booking quantity")
                print("➕ ADD EVENT <title> <venue> <location> <start_date> <end_date> <price_min> <price_max> <available_tickets> - Add a new event")
                print("🚪 exit - Exit the CLI")
                continue
            
            # Parse and execute the command
            try:
                result = parser.parse(user_input)
                if result:
                    print(result)
            except Exception as e:
                print(f"❌ Error executing command: {e}")
                
        except KeyboardInterrupt:
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()