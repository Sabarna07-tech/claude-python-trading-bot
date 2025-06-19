# src/kite_utils.py
import os
import sys
from pathlib import Path
from kiteconnect import KiteConnect
from dotenv import load_dotenv

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.schemas import PlaceOrderInput, GetPositionsOutput

# Load environment variables from the .env file
load_dotenv()

class KiteHelper:
    def __init__(self):
        """Initializes the KiteHelper and sets up the Kite Connect client."""
        api_key = os.getenv("KITE_API_KEY")
        access_token = os.getenv("KITE_ACCESS_TOKEN")

        if not api_key or not access_token:
            raise ValueError("KITE_API_KEY and KITE_ACCESS_TOKEN must be set in the .env file.")

        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        print("Kite Connect client initialized successfully.")

    def place_order(self, order_details: PlaceOrderInput) -> dict:
        """
        Places an order using the Kite Connect API.
        This is a synchronous function that will be called from an async tool handler.
        """
        try:
            # Map Pydantic model fields to the parameters expected by pykiteconnect
            order_params = {
                "exchange": order_details.exchange,
                "tradingsymbol": order_details.tradingsymbol,
                "transaction_type": self.kite.TRANSACTION_TYPE_BUY if order_details.transaction_type == 'BUY' else self.kite.TRANSACTION_TYPE_SELL,
                "quantity": order_details.quantity,
                "product": self.kite.PRODUCT_CNC if order_details.product == 'CNC' else self.kite.PRODUCT_MIS,
                "order_type": self.kite.ORDER_TYPE_MARKET if order_details.order_type == 'MARKET' else self.kite.ORDER_TYPE_LIMIT,
                "price": order_details.price,
                "variety": self.kite.VARIETY_REGULAR,
            }

            # The kite.place_order method requires 'price' to be absent for MARKET orders.
            if order_params["order_type"] == self.kite.ORDER_TYPE_MARKET:
                del order_params["price"]

            print(f"Placing order with params: {order_params}")
            # This is a blocking, synchronous network call.
            order_id = self.kite.place_order(**order_params)
            print(f"Successfully placed order. Order ID: {order_id}")
            
            # Ensure the returned order_id is a string to match the Pydantic schema
            return {"order_id": str(order_id)}

        except Exception as e:
            print(f"Error placing order: {e}")
            # Re-raise the exception to be caught by the MCP tool handler
            raise

    def get_positions(self) -> dict:
        """
        Fetches the user's current positions from the Kite Connect API.
        """
        try:
            # This is a blocking, synchronous network call.
            positions = self.kite.positions()
            print("Successfully fetched positions.")
            
            # Use Pydantic to validate the response and convert it to a dict.
            validated_positions = GetPositionsOutput.model_validate(positions)
            return validated_positions.model_dump()
        except Exception as e:
            print(f"Error fetching positions: {e}")
            raise
