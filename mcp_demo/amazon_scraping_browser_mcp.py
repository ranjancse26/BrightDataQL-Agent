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
      LET amazon = scraping_browser_navigate("https://www.amazon.com")
      THEN scraping_browser_type("input[name='field-keywords']", "wireless earbuds")
      THEN scraping_browser_click("input[type='submit']")
      THEN scraping_browser_wait_for("div[data-component-type='s-search-result']")
      THEN scraping_browser_click("div[data-component-type='s-search-result'] a.a-link-normal")
      THEN scraping_browser_wait_for("#productTitle")
      LET title = scraping_browser_get_text("#productTitle")
      LET price = scraping_browser_get_text(".a-price .a-offscreen")
      LET description = scraping_browser_get_text("#feature-bullets")

    RETURN {
      "title": title,
      "price": price,
      "description": description
    }
    END
    """

    result = await agent.run(query)
    print("Structured Output:\n", result)

  except Exception as e:
    logfire.exception("Amazon Scraping Browser Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
