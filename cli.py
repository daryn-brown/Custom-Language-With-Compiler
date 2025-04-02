# cli.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load environment variables (e.g., GEMINI_API_KEY in .env)
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")  

def suggest_next_command(user_input: str) -> str:
    """
    Simple function to get a command suggestion from Gemini
    based on the user's partial input.
    """
    prompt = f"""
You are a CLI command suggestion assistant for a Ticket Booking system.
The user typed: '{user_input}'
Suggest the most likely *complete* command they want to execute.
Possible commands include:
- LIST EVENTS IN "Kingston"
- BOOK "Coldplay Concert" ON YYYY-MM-DD FOR "Alice"
- CANCEL BOOKING 123
- CONFIRM BOOKING 123
- PAY FOR BOOKING 123
- UPDATE EVENT "Coldplay Concert" WITH 10 NEW TICKETS
Only return the completed command, no additional text.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip().strip("`")
    except Exception as e:
        return f"⚠️ Gemini Error: {e}"

def main():
    print("🎟️ Welcome to the Ticket Booking System CLI with Gemini Suggestions!")
    print("Type your command or 'exit' to quit.")
    print("Type 'suggest <partial>' to explicitly request a suggestion.\n")

    while True:
        try:
            user_input = input(">> ").strip()
            if user_input.lower() == "exit":
                print("Bye!")
                break

            # 1) If user explicitly asks: "suggest <partial>"
            if user_input.lower().startswith("suggest "):
                partial_input = user_input[8:]
                suggestion = suggest_next_command(partial_input)
                print(f"🤖 Gemini Suggests: {suggestion}")
                continue

            # 2) Otherwise, for very short input, automatically suggest
            #    e.g., user just typed "BOOK" or "LIST"
            if len(user_input.split()) < 3:
                suggestion = suggest_next_command(user_input)
                if suggestion:
                    print(f"🤖 Gemini Suggests: {suggestion}")

            # Normally, here is where you'd parse or handle the user command
            # For demonstration, we'll just echo it back:
            print(f"You entered: {user_input}")

        except EOFError:
            break

if __name__ == "__main__":
    main()
