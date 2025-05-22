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

        url = "https://remoteok.com/remote-python-jobs"

        position = 'Remote Python Developer'

        schema = """
        {
            jobs[] {
                job_title
                company_name
                tags[]
                location
                salary (if not available, use "n/a")
                job_description (short summary if possible)
                apply_link
                posted_date
                company_logo_url (if available, else use "n/a")
            }
        }
        """

        prompt = f"""
        Discover and extract real-time job listings for {position} roles from the web using the schema below. Access dynamic, JavaScript-rendered job listings and interact as a human would if needed.

        Your mission is to extract structured listing data using the schema below. Do **not rely solely on CSS selectors**. If standard element-based targeting fails, fallback to:

        You will be given an url {url} for the data extraction. Make sure to use the markdown tool.

        Your mission is to structured job listings 
        ## SCHEMA

        {schema}

        ## NOTES

        - If CSS selectors are unreliable, fall back to XPath for locating key fields.
        - Interact with the site if required to load content dynamically (e.g., scrolling, clicking "load more").
        - Extract only valid job listings (exclude ads or duplicate blocks).
        - Ensure structured output in a JSON-style format matching the schema.

        Output only in JSON format.
        """

        # Run query
        result = await agent.run(
            prompt,
            max_steps=max_steps,
        )
        print(f"\nResult: {result}")
    except Exception as e:
        logfire.exception("Recruitement Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
