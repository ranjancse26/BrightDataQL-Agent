import os
import re
import sys
from dotenv import load_dotenv
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent import AgentType
from langchain_google_genai import ChatGoogleGenerativeAI

one_levels_up = os.path.abspath(os.path.join(__file__, "../../"))
sys.path.insert(0, one_levels_up)

from tools.brightdataql_scraper_agent import BrightQLAgentScraperTool

def parse_and_run(tool: BrightQLAgentScraperTool, input_text: str, isHTML : bool) -> str:
    """
    Parses input_text to extract url and schema, then calls tool._run(url, schema).
    Expects input_text to contain lines like:

    url: <url_here>

    schema:
    <schema_here>
    """
    url_match = re.search(r"url:\s*(\S+)", input_text)
    schema_match = re.search(r"schema:\s*(.*)", input_text)

    if not url_match or not schema_match:
        raise ValueError("Input must contain 'url:' and 'schema:' sections")

    url = url_match.group(1)
    schema = schema_match.group(1).strip()

    return tool._run(url, isHTML, schema)


def create_agent(isHtml: bool):
    bright_token = os.getenv("BRIGHT_DATA_API_TOKEN")
    gemini_token = os.getenv("GEMINI_API_KEY")
    gemini_model = os.getenv("GOOGLE_GEMINI_MODEL_NAME")

    if not bright_token:
        raise ValueError("BRIGHT_DATA_API_TOKEN missing in environment")
    if not gemini_token:
        raise ValueError("GEMINI_API_KEY missing in environment")

    tool = BrightQLAgentScraperTool(bright_token=bright_token, gemini_token=gemini_token)

    tools = [
        Tool.from_function(
            func=lambda input_text: parse_and_run(tool, input_text, isHtml),
            name=tool.name,
            description=tool.description,
            args_schema=None,
        )
    ]
    
    llm = ChatGoogleGenerativeAI(model=gemini_model, temperature=0, api_key=os.environ["GEMINI_API_KEY"])

    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    return agent_executor


if __name__ == "__main__":
    load_dotenv()

    agent = create_agent(False)

    URL = "https://www.google.com/maps/search/boba+tea/@37.4400289,-122.1653309,14z/data=!3m1!4b1?entry=ttu&g_ep=EgoyMDI1MDIxMS4wIKXMDSoASAFQAw%3D%3D"

    SCHEMA = """
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

    PROMPT = f"""
    Use the `brightdata_agentql_scraper` tool to extract structured data.

    url: {URL}

    schema:
    {SCHEMA}
    """

    result = agent.run(PROMPT)
    print("\nFinal Result:\n", result)
