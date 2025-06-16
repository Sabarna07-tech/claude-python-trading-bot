from kiteconnect import KiteConnect
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# Get your API key and secret from environment variables
api_key = os.getenv("KITE_API_KEY")
api_secret = os.getenv("KITE_API_SECRET")

# Create a KiteConnect instance
kite = KiteConnect(api_key=api_key)

# Get the request_token from user input
request_token = input("Please paste the request_token here: ")

try:
    # Generate the session and get the access_token
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    
    print("\nSUCCESS!")
    print(f"Your Access Token is: {access_token}")
    print("\nCopy this token and paste it into your .env file for KITE_ACCESS_TOKEN.")

except Exception as e:
    print(f"\nAn error occurred: {e}")