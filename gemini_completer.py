from prompt_toolkit.completion import Completer, Completion
from gemini_utils import suggest_next_command
import time
import re

class GeminiCompleter(Completer):
    """
    A custom Completer that calls Gemini for suggestions
    based on the user's partial command.
    """
    def __init__(self):
        self.cache = {}
        self.last_call_time = 0
        self.debounce_delay = 0.05  # 50ms
        
        # Pattern to sanitize input
        self.control_char_pattern = re.compile(r'[\x00-\x1F\x7F]')
        
        # Command completions
        self.commands = {
            "L": "LIST",
            "LI": "LIST",
            "LIS": "LIST",
            "LIST": "LIST EVENTS",
            "B": "BOOK",
            "BO": "BOOK",
            "BOO": "BOOK",
            "BOOK": "BOOK",
            "C": "C",
            "CO": "CONFIRM",
            "CON": "CONFIRM",
            "CONF": "CONFIRM",
            "CONFI": "CONFIRM",
            "CONFIR": "CONFIRM",
            "CONFIRM": "CONFIRM",
            "CA": "CANCEL",
            "CAN": "CANCEL",
            "CANC": "CANCEL",
            "CANCE": "CANCEL",
            "CANCEL": "CANCEL",
            "P": "PAY",
            "PA": "PAY",
            "PAY": "PAY",
            "U": "UPDATE",
            "UP": "UPDATE",
            "UPD": "UPDATE",
            "UPDA": "UPDATE",
            "UPDAT": "UPDATE",
            "UPDATE": "UPDATE",
            "A": "ADD",
            "AD": "ADD",
            "ADD": "ADD EVENT"
        }
        
        # Command format examples to guide users
        self.command_formats = {
            "LIST": ["LIST EVENTS", "LIST EVENTS IN \"Location\""],
            "BOOK": ["BOOK \"Event Name\" ON YYYY-MM-DD FOR \"Person Name\"", "BOOK \"Event ID\" 2"],
            "CONFIRM": ["CONFIRM \"QTX-1234\""],
            "CANCEL": ["CANCEL \"QTX-1234\""],
            "PAY": ["PAY \"QTX-1234\" 100"],
            "UPDATE": ["UPDATE \"Event ID\" 50"],
            "ADD": ["ADD EVENT \"Title\" \"Venue\" \"Location\" YYYY-MM-DD YYYY-MM-DD 50 100 100"]
        }

    def get_completions(self, document, complete_event):
        """Get completions for the current input."""
        # Get the text at cursor position, without leading/trailing whitespace
        user_input = document.text_before_cursor.rstrip()
        
        # Clean any control characters
        user_input = self.control_char_pattern.sub('', user_input)
        
        if not user_input:
            # When empty, suggest all main commands
            for cmd, formats in self.command_formats.items():
                yield Completion(
                    text=formats[0],
                    start_position=0,
                    display=formats[0],
                    style="fg:green"
                )
            return
            
        # Check if the input is a known command prefix
        user_upper = user_input.upper()
        words = user_upper.split()
        first_word = words[0] if words else ""
        
        # Skip suggestions when inside quotes to improve typing speed
        if user_input.count('"') % 2 == 1:  # Inside quotes, don't suggest
            return
            
        # Skip suggestions when typing dates
        if len(words) > 3 and any(w for w in words if '-' in w and len(w) >= 4):
            # Likely typing a date, don't slow down with suggestions
            return
        
        if first_word in self.commands:
            # Get the full command
            full_cmd = self.commands[first_word]
            
            # If the user has just typed a short prefix, suggest the full command
            if len(words) == 1:
                # First, offer to complete the command word
                remainder = full_cmd[len(first_word):]
                if remainder:
                    yield Completion(
                        text=remainder,
                        start_position=0,
                        display=remainder,
                        style="fg:green"
                    )
                
                # Then suggest full command formats
                cmd_key = full_cmd.split()[0]  # Get the main command (LIST, BOOK, etc.)
                if cmd_key in self.command_formats:
                    for format in self.command_formats[cmd_key]:
                        # Only show format if it starts with what user typed
                        if format.startswith(user_upper):
                            # Show the full format as a suggestion
                            yield Completion(
                                text=format[len(user_input):],
                                start_position=0,
                                display=f"Example: {format}",
                                style="fg:yellow"
                            )
                return
        
        # Fast return for common command patterns
        if (len(words) >= 2 and 
            (first_word == "BOOK" and len(words) >= 3) or  # BOOK command with args
            (first_word == "LIST" and len(words) >= 2) or  # LIST command with args
            (" ON " in user_upper) or  # Typing a date
            (" FOR " in user_upper) or  # Typing a name
            ('"' in user_input)):  # Typing quoted text
            # Quick exit for faster typing in these scenarios
            return
        
        # For more complex completions or longer inputs, try Gemini API
        # But only for simpler cases or at word boundaries
        if len(user_input) >= 2 and user_input.endswith((' ')):
            current_time = time.time()
            
            # Check cache
            if user_input in self.cache:
                suggestion, timestamp = self.cache[user_input]
                if current_time - timestamp < 300 and not suggestion.startswith("⚠️"):
                    # Use the cached suggestion
                    if suggestion.startswith(user_input):
                        # Just return the remainder (most common case)
                        remainder = suggestion[len(user_input):]
                        if remainder:
                            yield Completion(
                                text=remainder,
                                start_position=0,
                                display=remainder,
                                style="fg:cyan"
                            )
                    else:
                        # This is where the "bash" prefix issue would happen
                        # Fix it by setting start_position to exact cursor column
                        yield Completion(
                            text=suggestion,
                            start_position=-document.cursor_position_col,
                            display=suggestion,
                            style="fg:cyan"
                        )
                    return
            
            # Increase debounce delay to reduce API calls
            effective_debounce = self.debounce_delay * 2 if len(words) > 2 else self.debounce_delay
            
            # Use Gemini API with debouncing, but only at word boundaries
            if current_time - self.last_call_time >= effective_debounce:
                try:
                    suggestion = suggest_next_command(user_input)
                    self.last_call_time = current_time
                    
                    # Clean and cache the suggestion
                    suggestion = self.control_char_pattern.sub('', suggestion)
                    self.cache[user_input] = (suggestion, current_time)
                    
                    if suggestion and not suggestion.startswith("⚠️"):
                        if suggestion.startswith(user_input):
                            # Just return the remainder
                            remainder = suggestion[len(user_input):]
                            if remainder:
                                yield Completion(
                                    text=remainder,
                                    start_position=0,
                                    display=remainder,
                                    style="fg:cyan"
                                )
                        else:
                            # Complete replacement - fix "bash" prefix issue
                            yield Completion(
                                text=suggestion,
                                start_position=-document.cursor_position_col,
                                display=suggestion,
                                style="fg:cyan"
                            )
                except Exception as e:
                    # Don't block the UI
                    print(f"Completion error: {e}") 