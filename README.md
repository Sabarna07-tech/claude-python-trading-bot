AI Trading Bot with Claude and Python (Official SDK)
This project is a Python implementation of an AI-powered trading bot that connects the Claude Large Language Model (LLM) to a Zerodha trading account. It uses the official Model Context Protocol (MCP) Python SDK to expose trading functions as "tools" that Claude can understand and execute based on natural language commands.

🔴 DISCLAIMER: This is for educational purposes only. Trading bots carry a high risk of financial loss. Do not use with real money without fully understanding the code and risks.

Features
Natural Language Trading: Use plain English in the Claude app to execute trades (e.g., "buy 10 shares of INFY at market price").

Real-time Data: Fetch and view your current trading positions.

Official SDK: Built with the mcp-sdk for robust and reliable communication with Claude.

Secure: Keeps your API keys and tokens local using a .env file.

Type-Safe: Uses Pydantic to ensure all data flowing between Claude and the trading API is correctly structured.

Project Structure
claude-python-trading-bot/
│
├── src/
│   ├── main.py             # Main application: MCP server logic using the SDK
│   ├── schemas.py          # Pydantic schemas for data validation
│   └── kite_utils.py       # Handles all Zerodha Kite Connect logic
│
├── .env                    # Stores secret API keys
├── requirements.txt        # Project dependencies
└── README.md               # This file

Setup and Installation
1. Prerequisites
Python 3.8+

A Zerodha developer account (developers.kite.trade) with an API key.

The Claude Desktop Application.

2. Clone and Setup
# Clone the repository (or set up the files manually)
git clone <your-repo-url>
cd claude-python-trading-bot

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies from the updated requirements file
pip install -r requirements.txt

3. Configure API Keys & Access Token
Create .env file: Create a file named .env in the root directory.

Add Credentials: Open the .env file and add your Zerodha API credentials:

KITE_API_KEY="your_api_key"
KITE_API_SECRET="your_api_secret"
KITE_ACCESS_TOKEN="your_access_token"

Get Access Token: The access_token must be generated daily. I have provided a separate explanation on how to get this token using a manual login and a helper script. You must update the KITE_ACCESS_TOKEN in your .env file each day.

How to Run
Start the MCP Server:
Run the main.py script from your terminal. The official SDK will handle the connection.

python src/main.py

The server will start and print a message like Starting MCP server, waiting for Claude to connect....

Connect from Claude:

Open the Claude Desktop Application.

Go to the settings for using local tools.

Configure it to use the python src/main.py command as the local tool server.
