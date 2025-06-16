# src/main.py
import asyncio
from mcp_sdk.mcp import McpServer
from mcp_sdk.stdio_transport import StdioServerTransport
from src.kite_utils import KiteHelper
from src.schemas import PlaceOrderInput, PlaceOrderOutput, GetPositionsOutput

# --- 1. Initialize API Helper ---
# Initialize the Kite Helper once when the script starts.
kite_helper = KiteHelper()

# --- 2. Create the MCP Server ---
# Use the StdioServerTransport, which allows the Claude desktop app
# to communicate with this Python script using standard input/output.
server = McpServer(transport=StdioServerTransport())

# --- 3. Define Tools ---
# Use the @server.tool decorator to define a function as a tool
# that the Claude LLM can invoke.

@server.tool(
    name="placeOrder",
    description="Places a stock order on the Zerodha trading platform. Use this for buying or selling stocks.",
    input_schema=PlaceOrderInput,
    output_schema=PlaceOrderOutput,
)
async def place_order(params: PlaceOrderInput):
    """
    This async function is the handler for the 'placeOrder' tool.
    The MCP SDK will automatically validate the incoming request against
    the PlaceOrderInput schema.
    """
    print(f"Tool 'placeOrder' invoked with params: {params}")
    try:
        # The actual API call is synchronous, but we call it from our async handler.
        result = kite_helper.place_order(params)
        return result
    except Exception as e:
        print(f"An error occurred in the 'placeOrder' tool: {e}")
        # The SDK will properly handle this exception and report it to the LLM.
        raise

@server.tool(
    name="getPositions",
    description="Fetches all current open trading positions from the Zerodha account.",
    output_schema=GetPositionsOutput,
)
async def get_positions():
    """
    This async function handles the 'getPositions' tool.
    It takes no input.
    """
    print("Tool 'getPositions' invoked.")
    try:
        result = kite_helper.get_positions()
        return result
    except Exception as e:
        print(f"An error occurred in the 'getPositions' tool: {e}")
        raise

# --- 4. Start the Server ---
async def main():
    """The main entry point to start the server."""
    print("Starting MCP server, waiting for Claude to connect...")
    await server.start()
    print("Server has stopped.")

if __name__ == "__main__":
    # Run the main async function.
    # This will start the server and keep it running until interrupted.
    asyncio.run(main())

