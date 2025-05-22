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

        url = "https://www.glossier.com/products/milky-jelly-cleanser"

        schema = """
        {
            products[] {
                name,
                price,
                size,
                ingredients[],
                reviews { average_rating, review_count },
                promo { discount_percentage, bundle_offer, login_required },
                availability
            }
        }
        """

        prompt = f"""
        You are a competitive intelligence agent.

        Your task is to extract structured product data from {url}.

        Use the schema below to extract key data including promo offers, availability, and user sentiment.  
        Simulate necessary interactions (e.g., consent clicks, page scrolling) and extract from JS-rendered sections if required.

        Schema:
        {schema}

        Output strictly in JSON. Do not include explanations.
        """

        # Run query
        result = await agent.run(
            prompt,
            max_steps=max_steps,
        )
        print(f"\nResult: {result}")

    except Exception as e:
        logfire.exception("Competitive Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
