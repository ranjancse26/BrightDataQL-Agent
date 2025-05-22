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

        url = "https://www.zocdoc.com/primary-care-doctors"

        schema = """
        {
            providers[] {
                name,
                specialty,
                rating,
                review_count,
                accepted_insurance[],
                appointments[] {
                    date,
                    time,
                    mode,
                    location,
                    availability_status
                }
            }
        }
        """

        prompt = f"""
        You are a healthcare data extractor bot.

        Your task is to extract structured provider information and real-time appointment availability from this page:  
        {url}

        Use the schema below to return information on primary care providers available in New York City.  
        Simulate required interactions like location filters, next-week calendar navigation, and selecting virtual visits.

        Schema:
        {schema}

        Output in JSON format only.
        """

        # Run query
        result = await agent.run(
            prompt,
            max_steps=max_steps,
        )
        print(f"\nResult: {result}")
    except Exception as e:
        logfire.exception("Healthcare Agent execution failed", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())
