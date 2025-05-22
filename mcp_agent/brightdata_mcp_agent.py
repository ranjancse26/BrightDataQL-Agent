"""
Bright Data Example for mcp_use with Google Gemini.
Please make sure to install Bright Data MCP Server
https://www.npmjs.com/package/@brightdata/mcp

"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient

def get_mcp_agent(max_steps: int):
    # Configure MCP Server
    config = {
        "mcpServers": {
            "Bright Data": {
                "command": "npx",
                "args": ["@brightdata/mcp"],
                "env": {
                    "API_TOKEN": os.environ["BRIGHT_DATA_API_TOKEN"],
                    "WEB_UNLOCKER_ZONE": os.environ["WEB_UNLOCKER_ZONE"],
                    "BROWSER_AUTH": os.environ["BROWSER_AUTH"]
                }
            }
        }
    }
    client = MCPClient.from_dict(config)

    os.environ["GOOGLE_API_KEY"] = os.environ["GEMINI_API_KEY"]

    # Set up the Gemini LLM (replace model name if needed)
    llm = ChatGoogleGenerativeAI(model=os.environ["GOOGLE_GEMINI_MODEL_NAME"], temperature=0, api_key=os.environ["GEMINI_API_KEY"])

    # Create MCP Agent
    agent = MCPAgent(llm=llm, client=client, max_steps=max_steps)

    return agent