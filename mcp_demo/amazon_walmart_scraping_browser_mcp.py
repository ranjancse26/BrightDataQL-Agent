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

    query = """
    BEGIN
      # Search on Amazon
      scraping_browser_navigate("https://www.amazon.com")
      scraping_browser_type("input[name='field-keywords']", "best wireless earbuds")
      scraping_browser_click("input[type='submit']")
      scraping_browser_wait_for("div[data-component-type='s-search-result']")
      scraping_browser_click("div[data-component-type='s-search-result']")
      scraping_browser_wait_for("#productTitle")

      LET amazon_name = scraping_browser_get_text("#productTitle")
      LET amazon_price = scraping_browser_get_text(".a-price .a-offscreen")
      LET amazon_rating = scraping_browser_get_text("span[data-asin][data-variation] span.a-icon-alt")

      # Search on Walmart
      scraping_browser_navigate("https://www.walmart.com")
      scraping_browser_type("input[name='query']", amazon_name)
      scraping_browser_click("button[type='submit']")
      scraping_browser_wait_for("a[data-type='itemTitles']")
      scraping_browser_click("a[data-type='itemTitles']")
      scraping_browser_wait_for("h1")

      LET walmart_name = scraping_browser_get_text("h1")
      LET walmart_price = scraping_browser_get_text("span[class*='price']")
      LET walmart_rating = scraping_browser_get_text("span[class*='stars']")

      # Logic to choose best deal
      LET best_store = IF(amazon_price < walmart_price, "Amazon", "Walmart")
      LET reason = IF(amazon_price < walmart_price, "Amazon has the lower price", "Walmart has the lower price")

    RETURN {
      "amazon_product": {
        "name": amazon_name,
        "price": amazon_price,
        "rating": amazon_rating
      },
      "walmart_product": {
        "name": walmart_name,
        "price": walmart_price,
        "rating": walmart_rating
      },
      "recommendation": {
        "best_store": best_store,
        "reason": reason
      }
    }
    END
    """

    result = await agent.run(query)
    print("==== Structured Response ====")
    print(result)

  except Exception as e:
    logfire.exception("Amazon Walmart Scraping Browser Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
