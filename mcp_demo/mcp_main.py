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

        url = "https://www.google.com/maps/search/boba+tea/@37.4400289,-122.1653309,14z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI1MDIxMS4wIKXMDSoASAFQAw%3D%3D"

        schema = """
        {
            listings[] {
                name
                rating(in stars)
                description(if not available, use "n/a")
                order_link(if not available, use "n/a")
                take_out_link(if not available, use "n/a")
                address
                hours
            }
        }
        """

        to_format = 'markdown'

        # Run query
        result = await agent.run(
            f"Scrape the provided {url} in {to_format} format and output the response in the following format {schema}. Make sure to integrate until you got a valid fully formatted JSON response.",
            max_steps=max_steps,
        )
        print(f"\nResult: {result}")
    except Exception as e:
        logfire.exception("MCP Main Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
