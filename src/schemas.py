# src/schemas.py
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class PlaceOrderInput(BaseModel):
    """
    Defines the structure for the input parameters required to place an order.
    This schema is used to validate the data sent from the Claude LLM.
    """
    tradingsymbol: str = Field(..., description="The trading symbol of the instrument (e.g., 'INFY', 'TCS').")
    exchange: Literal['NSE', 'BSE'] = Field(..., description="The exchange on which to place the order (e.g., 'NSE').")
    transaction_type: Literal['BUY', 'SELL'] = Field(..., description="The type of transaction.")
    order_type: Literal['MARKET', 'LIMIT'] = Field(..., description="The type of order.")
    quantity: int = Field(..., gt=0, description="The number of shares to trade.")
    product: Literal['CNC', 'MIS'] = Field(..., description="Product type: CNC (for delivery) or MIS (for intraday).")
    price: Optional[float] = Field(None, description="The price for a LIMIT order. Not required for MARKET orders.")

class PlaceOrderOutput(BaseModel):
    """
    Defines the structure for the output after placing an order.
    """
    order_id: str = Field(..., description="The unique ID of the placed order.")

class Position(BaseModel):
    """
    Defines the structure for a single trading position.
    """
    tradingsymbol: str
    exchange: str
    instrument_token: int
    product: str
    quantity: int
    overnight_quantity: int
    multiplier: float
    average_price: float
    close_price: float
    last_price: float
    value: float
    pnl: float
    m2m: float
    unrealised: float
    realised: float

class GetPositionsOutput(BaseModel):
    """
    Defines the structure for the list of all trading positions.
    """
    net: List[Position] = Field(..., description="List of net positions.")
    day: List[Position] = Field(..., description="List of positions for the day.")