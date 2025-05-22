import os
import sys
import asyncio
import logfire
from dotenv import load_dotenv

load_dotenv()

one_levels_up = os.path.abspath(os.path.join(__file__, "../../"))
sys.path.insert(0, one_levels_up)

from mcp_agent.brightdata_mcp_agent import get_mcp_agent
from observability import mcplogfire

async def main():
    try:
        mcplogfire.init()
        max_steps = int(os.environ["MAX_MCP_AGENT_STEPS"])

        # Create MCP Agent
        agent = get_mcp_agent(max_steps)

        url = "https://finance.yahoo.com/quote/AAPL"

        schema = """
        {
            "company": {
                "name": "string",
                "ticker": "string",
                "exchange": "string (e.g., NASDAQ, NYSE)"
            },
            "stock_quote": {
                "price": "float",
                "change": "float",
                "change_percent": "string",
                "last_updated": "string (e.g., 2024-10-01T15:30:00Z)"
            },
            "key_metrics": {
                "market_cap": "string",
                "pe_ratio": "float",
                "eps": "float",
                "dividend_yield": "string",
                "52_week_range": "string"
            },
            "analyst_rating": {
                "consensus": "string (e.g., Buy, Hold, Sell)",
                "price_target_high": "float",
                "price_target_low": "float",
                "price_target_avg": "float"
            },
            "recent_earnings": [
                {
                "quarter": "string (e.g., Q2 2024)",
                "date": "YYYY-MM-DD",
                "actual_eps": "float",
                "expected_eps": "float",
                "revenue": "string"
                }
            ]
        }
        """

        prompt = f"""
        You are a structured financial data extractor.

        Your mission is to extract key stock market and company financial information from complex, JavaScript-rendered HTML content of a financial website like Yahoo Finance, MarketWatch, or Bloomberg.

        Your mission is to extract structured listing data using the schema below. Do **not rely solely on CSS selectors**. If standard element-based targeting fails, fallback to:

        - XPath expressions
        - Nearby text-based anchors
        - Semantic matching of content blocks

        You will be provided with the url {url}. These pages may be deeply nested, have interactive elements, and may not use well-formed labels or semantic markup.

        Use a robust approach:
        - Prefer **XPath** over CSS selectors.
        - Extract text by **semantic meaning**, visual proximity, and patterns.
        - Do not depend on form labels or attributes.
        - Use "n/a" for missing values.
        - Be strict with format and match the schema exactly.

        Schema

        {schema}

        Output only in JSON format.
        """

        # Run query
        result = await agent.run(
            prompt,
            max_steps=max_steps,
        )
        print(f"\nResult: {result}")
    except Exception as e:
        logfire.exception("Financial Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
