import os
import sys
from dotenv import load_dotenv
from parser import parser

# Ensure UTF-8 encoding for Unicode support
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def main():
    print("🎫 Welcome to QuickTix CLI!")
    print("ℹ️ Type 'help' for available commands or start typing to see suggestions.")
    print("💡 Type 'exit' to quit the CLI.")

    while True:
        try:
            # Get user input
            user_input = input("QuickTix> ").strip()
            
            if not user_input:
                continue

            # Parse and execute the command
            try:
                result = parser.parse(user_input)
                if result:
                    print(result)
            except Exception as e:
                print(f"❌ Error executing command: {e}")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()