# Group Members: 
# Justin Alder 2007273
# Daryn Brown 2002414
# Marvis Haughton 1802529
# Peta Gaye Mundle 1403906 
# Cassandra Powell 2005742

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import os

app = FastAPI()

# Allow frontend to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve static files from /static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

class Command(BaseModel):
    command: str

@app.post("/run", response_class=PlainTextResponse)
async def run_command(cmd: Command):
    try:
        # First, try to directly import and use the parser
        try:
            from parser import parser
            result = parser.parse(cmd.command)
            if result:
                print(f"Direct parser result: {result}")
                return result
        except Exception as direct_error:
            print(f"Error using direct parser: {str(direct_error)}")
        
        # Fallback to subprocess approach
        print(f"Running command via subprocess: {cmd.command}")
        result = subprocess.run(
            ["python", "cli.py"],
            input=cmd.command.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        output = result.stdout.decode() + result.stderr.decode()
        print(f"Subprocess output: {output}")
        return output
    except Exception as e:
        print(f"Run command error: {str(e)}")
        return f"Error: {str(e)}"

@app.get("/suggest/{partial_command}", response_class=PlainTextResponse)
async def get_suggestions(partial_command: str):
    try:
        # Try to use the Gemini API first
        try:
            from gemini_utils import suggest_next_command
            suggestion = suggest_next_command(partial_command)
            print(f"Gemini suggestion for '{partial_command}': {suggestion}")
            return suggestion
        except Exception as e:
            print(f"Error using Gemini: {str(e)}")
            
        # Fallback to basic suggestion logic
        partial_upper = partial_command.upper()
        
        # Basic suggestion templates - plain text only
        suggestions = {
            "LI": "LIST EVENTS",
            "LIST": "LIST EVENTS",
            "LIST E": "LIST EVENTS",
            "LIST EV": "LIST EVENTS",
            "LIST EVE": "LIST EVENTS",
            "LIST EVEN": "LIST EVENTS",
            "LIST EVENT": "LIST EVENTS",
            "LIST EVENTS I": "LIST EVENTS IN \"Kingston\"",
            "BO": "BOOK \"Event Name\" ON 2024-12-31 FOR \"Person Name\"",
            "BOO": "BOOK \"Event Name\" ON 2024-12-31 FOR \"Person Name\"",
            "BOOK": "BOOK \"Event Name\" ON 2024-12-31 FOR \"Person Name\"",
            "CONF": "CONFIRM \"QTX-1234\"",
            "CONFI": "CONFIRM \"QTX-1234\"",
            "CONFIR": "CONFIRM \"QTX-1234\"",
            "CONFIRM": "CONFIRM \"QTX-1234\"",
            "PAY": "PAY \"QTX-1234\" 100",
            "CAN": "CANCEL \"QTX-1234\"",
            "CANC": "CANCEL \"QTX-1234\"",
            "CANCE": "CANCEL \"QTX-1234\"",
            "CANCEL": "CANCEL \"QTX-1234\"",
            "UPD": "UPDATE EVENT \"Event Name\" WITH 10 NEW TICKETS",
            "UPDA": "UPDATE EVENT \"Event Name\" WITH 10 NEW TICKETS",
            "UPDAT": "UPDATE EVENT \"Event Name\" WITH 10 NEW TICKETS",
            "UPDATE": "UPDATE EVENT \"Event Name\" WITH 10 NEW TICKETS",
            "AD": "ADD EVENT \"Title\" AT \"Venue\" IN \"Location\" FROM 2024-12-31 TO 2024-12-31 PRICE 50 TO 100",
            "ADD": "ADD EVENT \"Title\" AT \"Venue\" IN \"Location\" FROM 2024-12-31 TO 2024-12-31 PRICE 50 TO 100"
        }
        
        # Find matches
        for key, value in suggestions.items():
            if partial_upper.startswith(key):
                print(f"Fallback suggestion for '{partial_command}': {value}")
                return value
        
        # If no match found and input is not too short
        if len(partial_command) >= 2:
            # Find the closest match
            for key in sorted(suggestions.keys(), key=len, reverse=True):
                if key.startswith(partial_upper):
                    print(f"Closest match suggestion for '{partial_command}': {suggestions[key]}")
                    return suggestions[key]
        
        return ""
    except Exception as e:
        print(f"Error in suggestion: {str(e)}")
        return f"Error getting suggestion: {str(e)}"