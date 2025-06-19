# src/main.py
import asyncio
from fastapi import FastAPI, HTTPException, Request
import uvicorn
import json
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.kite_utils import KiteHelper
from src.schemas import PlaceOrderInput, PlaceOrderOutput, GetPositionsOutput

# --- 1. Initialize API Helper ---
# Initialize the Kite Helper once when the script starts.
kite_helper = KiteHelper()

# --- 2. Create the FastAPI Server ---
app = FastAPI(
    title="Claude Python Trading Bot",
    description="An API server to expose Zerodha trading functions for Claude LLM",
    version="1.0.0",
)

# --- 3. Define API Endpoints ---
@app.post("/api/place_order", response_model=PlaceOrderOutput)
async def place_order(params: PlaceOrderInput):
    """
    Places a stock order on the Zerodha trading platform.
    """
    print(f"Endpoint 'place_order' invoked with params: {params}")
    try:
        result = kite_helper.place_order(params)
        return result
    except Exception as e:
        print(f"An error occurred in the 'place_order' endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_positions", response_model=GetPositionsOutput)
async def get_positions():
    """
    Fetches all current open trading positions from the Zerodha account.
    """
    print("Endpoint 'get_positions' invoked.")
    try:
        result = kite_helper.get_positions()
        return result
    except Exception as e:
        print(f"An error occurred in the 'get_positions' endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    Root endpoint for the API server.
    """
    return {
        "name": "Claude Python Trading Bot API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/place_order", "method": "POST", "description": "Places a stock order"},
            {"path": "/api/get_positions", "method": "GET", "description": "Gets current positions"}
        ]
    }

# --- 4. Start the Server ---
def start_server(host="127.0.0.1", port=None):
    """Start the FastAPI server with uvicorn"""
    # Try to find an available port if none is specified
    if port is None:
        # Try ports 8000 through 8010
        for p in range(8000, 8011):
            try:
                print(f"Starting API server at http://{host}:{p}")
                uvicorn.run(app, host=host, port=p)
                break
            except OSError as e:
                print(f"Port {p} is not available. Trying next port...")
                if p == 8010:
                    print("All ports from 8000 to 8010 are in use. Please free up a port and try again.")
                    sys.exit(1)
    else:
        try:
            print(f"Starting API server at http://{host}:{port}")
            uvicorn.run(app, host=host, port=port)
        except OSError as e:
            print(f"Error starting server on port {port}: {e}")
            sys.exit(1)

# For the CLI script
def main():
    """Start the server with default settings"""
    # Can take optional port from command line
    port = None
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
            
    start_server(port=port)

if __name__ == "__main__":
    # Run the main function.
    main()

