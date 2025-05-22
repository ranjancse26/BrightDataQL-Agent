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

        url = "https://www.zillow.com/homes/for_sale/San-Francisco_rb/"

        schema = """
        {
            listings[] {
                price,
                address,
                bedrooms,
                bathrooms,
                area_sqft,
                status,
                days_on_market,
                listing_agent {
                name,
                phone,
                agency
                },
                property_url,
                price_history[] {
                date,
                event,
                price
                }
            }
        }
        """

        prompt = f"""
        You are a real estate property data extractor.

        You will be given an url {url} of a real estate search results page (e.g., Zillow, Redfin, Realtor.com). These websites often use React-based rendering and do not associate labels and input fields clearly.

        Your mission is to extract structured listing data using the schema below. Do **not rely solely on CSS selectors**. If standard element-based targeting fails, fallback to:

        - XPath expressions
        - Nearby text-based anchors
        - Semantic matching of content blocks

        You should **not stop** if perfect structure is not found—try alternate methods (including inferred DOM structure or visual position). Use approximate matches and explain where assumptions were made.

        Do not depend on labels being directly linked to inputs.

        ### Sample HTML context:
        - Listings are inside cards or tiles
        - Prices, bedrooms, and area are shown visibly
        - Agent/contact info may be in a footer or modal

        ---
        ### SCHEMA:
        {schema}
        ---

        Your response should be ONLY the extracted data in JSON format.

        Ignore boilerplate HTML like header, navbar, cookie notices, etc.

        If some fields like price history or phone numbers are not found, use `"n/a"`.

        Output only in JSON format.
        """

        # Run query
        result = await agent.run(
            prompt,
            max_steps=max_steps,
        )
        print(f"\nResult: {result}")
    except Exception as e:
        logfire.exception("Realestate Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
