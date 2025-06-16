# 🤖 Claude-Python Trading Bot

This project is a **Python implementation of an AI-powered trading bot** that connects the **Claude Large Language Model (LLM)** to a **Zerodha trading account**. It leverages the official **Model Context Protocol (MCP) SDK** to expose trading functions as "tools" that Claude can understand and execute using natural language.

> ⚠️ **DISCLAIMER:**  
> This bot is for educational purposes only. Trading involves financial risk. Do **NOT** use with real money unless you fully understand the code and accept the risks.

---

## ✨ Features

- 🗣 **Natural Language Trading:**  
  Use plain English to place trades through Claude (e.g., "Buy 10 shares of INFY at market price").

- 🔄 **Real-time Data:**  
  View your current trading positions and holdings via Claude.

- ✅ **Official SDK Integration:**  
  Built with the [mcp-sdk](https://github.com/anthropic/mcp) for reliable Claude communication.

- 🔐 **Secure:**  
  Keeps API keys and tokens secure using a `.env` file.

- 🧠 **Type-Safe:**  
  Utilizes [Pydantic](https://docs.pydantic.dev/) for data validation and structure.

---

## 🗂 Project Structure

```
claude-python-trading-bot/
│
├── src/
│   ├── main.py           # Main MCP server logic
│   ├── kite_utils.py     # Zerodha Kite Connect logic
│   └── schemas.py        # Pydantic schemas
│
├── .env                  # Secret API keys and tokens (not committed)
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🛠 Setup and Installation

### ✅ Prerequisites

- Python 3.8+
- Zerodha Developer Account: [developers.kite.trade](https://developers.kite.trade/)
- Claude Desktop Application (with local tool support)

### 🚀 Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/claude-python-trading-bot.git
   cd claude-python-trading-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys & Access Token**

   Create a `.env` file in the root directory:

   ```
   KITE_API_KEY="your_api_key"
   KITE_API_SECRET="your_api_secret"
   KITE_ACCESS_TOKEN="your_daily_access_token"
   ```

   > 🔁 You must update the `KITE_ACCESS_TOKEN` daily.  
   > A helper script is included to generate this using manual login.

---

## ▶️ How to Run

1. **Start the MCP server:**
   ```bash
   python src/main.py
   ```
   You should see:
   ```
   Starting MCP server, waiting for Claude to connect...
   ```

2. **Connect from Claude Desktop App**

   - Open Claude Desktop
   - Go to Settings → Local Tools
   - Set the command to run the local tool server as:
     ```bash
     python src/main.py
     ```

---

## 📌 Notes

- MCP SDK handles the communication between Claude and your trading tools.
- The `.env` file should **never** be committed to version control.
- Ensure your API credentials are correct and updated.
- Use sandbox/testing mode until you're confident the bot works as expected.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

Built by _Your Name_.  
Inspired by the potential of LLMs + real-world trading tools.

---

## 🧪 Example `.env` file

```ini
KITE_API_KEY="kiteapikey123"
KITE_API_SECRET="kitesecret456"
KITE_ACCESS_TOKEN="your_access_token_here"
```

---

## 🖥️ Example CLI Usage

- **Buy shares via Claude:**  
  “Buy 10 shares of INFY at market price.”

- **Check portfolio positions:**  
  “Show me my current holdings.”

- **Sell a stock:**  
  “Sell 5 shares of TCS at limit price 3600.”

---

Let me know if you'd like to see more CLI usage examples or a sample `.env` file!
