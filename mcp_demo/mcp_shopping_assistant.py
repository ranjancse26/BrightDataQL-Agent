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
    agent = get_mcp_agent(max_steps)

    prompt = """
    You are an intelligent shopping assistant.

    Task:
    1. Search Amazon for "best wireless earbuds".
    2. Extract top product details:
        - name
        - price
        - rating
        - review_count
        - features
        - availability
    3. Using the top product's name, perform a search on Walmart.
    4. Find a matching or equivalent product on Walmart and extract the same details.
    5. Compare the Amazon and Walmart listings.
    6. Recommend the better deal (consider price, rating, reviews, features).

    Output Format (strict JSON):
    {
      "amazon_product": {
        "name": "...",
        "price": "...",
        "rating": "...",
        "review_count": "...",
        "features": "...",
        "availability": "..."
      },
      "walmart_product": {
        "name": "...",
        "price": "...",
        "rating": "...",
        "review_count": "...",
        "features": "...",
        "availability": "..."
      },
      "recommendation": {
        "best_store": "...",  // either "Amazon" or "Walmart"
        "reason": "..."
      }
    }
    """

    result = await agent.run(prompt)
    print("==== Result ====")
    print(result)
  except Exception as e:
    logfire.exception("Shopping Assistant Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
