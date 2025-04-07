# 🎫 QuickTix-SadeScript

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-modern-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern ticket booking system with AI-powered command suggestions

</div>

---

## 🌟 Overview

QuickTix-SadeScript is a ticket booking system with a custom domain-specific language (DSL) implementation and an AI-powered CLI interface. The project combines a custom language parser with Google's Gemini AI to provide intelligent command suggestions for ticket booking operations.

## ✨ Features

🎯 Custom DSL for ticket booking operations  
🤖 AI-powered command suggestions using Google's Gemini  
💻 Interactive CLI with intelligent auto-completion  
🚀 FastAPI backend server for web interface  
🔧 Comprehensive lexer and parser implementation  
🧪 Built-in test suite

## 📋 Prerequisites

- 🐍 Python 3.x
- 📦 pip (Python package manager)
- 🔑 Google Gemini API key

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/QuickTix-SadeScript.git
cd QuickTix-SadeScript
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Windows Setup (if needed)

If you get "'uvicorn' is not recognized" error, you'll need to add Python Scripts to your PATH:

#### a. Locate your Scripts directory

```bash
python -c "import sys; print(sys.executable.replace('python.exe', 'Scripts'))"
```

#### b. Add to PATH (choose one):

**Temporary (current session):**

```bash
set PATH=%PATH%;C:\Users\YourUsername\AppData\Local\Programs\Python\Python3x\Scripts
```

**Permanent (recommended):**

1. Open System Properties (Win + Pause/Break)
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System Variables", find "Path"
5. Click "Edit" and "New"
6. Add your Python Scripts path
7. Click "OK" on all windows
8. Restart your terminal

## 📁 Project Structure

```
QuickTix-SadeScript/
├── cli.py           # Interactive CLI with AI suggestions
├── lexer.py         # Language lexer implementation
├── parser.py        # Language parser implementation
├── main.py          # FastAPI web server
├── test_lexer.py    # Lexer unit tests
├── test_parser.py   # Parser unit tests
├── static/          # Web interface assets
└── requirements.txt # Project dependencies
```

## 🎮 Usage

### 🖥️ CLI Interface

1. **Start the CLI:**

```bash
python cli.py
```

2. **Available Commands:**

```
📋 LIST EVENTS IN "Location"
🎟️ BOOK "Event Name" ON YYYY-MM-DD FOR "Person"
❌ CANCEL BOOKING <id>
✅ CONFIRM BOOKING <id>
💳 PAY FOR BOOKING <id>
📝 UPDATE EVENT "Event Name" WITH <number> NEW TICKETS
```

3. **Command Suggestions:**

- Type `suggest` followed by a partial command for AI suggestions
- Short commands automatically trigger suggestions
- Type `exit` to quit

### 🌐 Web Interface

1. **Start the server** (choose one method):

   💫 **Standard method** (requires Python Scripts in PATH):

   ```bash
   uvicorn main:app --reload
   ```

   ⚡ **Alternative method:**

   ```bash
   python -m uvicorn main:app --reload
   ```

2. Open your browser to `http://localhost:8000`

## 🧪 Running Tests

```bash
python -m pytest test_lexer.py test_parser.py
```

## 📚 Dependencies

- 🚀 **FastAPI** - Modern web framework
- 🌐 **uvicorn** - Lightning-fast ASGI server
- 🔍 **PLY** - Python Lex-Yacc parsing tools
- 🔐 **python-dotenv** - Environment management
- 🤖 **google-generativeai** - Gemini AI SDK
- 🗄️ **azure-cosmos** - Azure Cosmos DB SDK
- 🧪 **pytest** - Testing framework

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 📄 License

This project is licensed under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- 🤖 Google Gemini AI for intelligent suggestions
- ⚡ FastAPI team for the excellent framework
- 🔧 PLY team for robust parsing tools

---

<div align="center">
Made with ❤️ by the QuickTix team
</div>
