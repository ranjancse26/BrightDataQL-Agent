import os
import requests
from pydantic import PrivateAttr, Field
from dataclasses import dataclass
from langchain.agents import Tool, initialize_agent
from langchain.agents.agent import AgentType
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

class BrightDataWebUnlocker:
    def __init__(self, api_token, zone="web_unlocker1"):
        self.api_token = api_token
        self.zone = zone

    def fetch_html(self, target_url: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        payload = {
            "zone": self.zone,
            "url": target_url,
            "format": "raw",
            "data_format": "html"
        }
        res = requests.post("https://api.brightdata.com/request", headers=headers, json=payload)
        res.raise_for_status()
        return res.text

    def fetch_markdown(self, target_url: str) -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        payload = {
            "zone": self.zone,
            "url": target_url,
            "format": "raw",
            "data_format": "markdown"
        }
        res = requests.post("https://api.brightdata.com/request", headers=headers, json=payload)
        res.raise_for_status()
        return res.text

class GeminiExtractor:
    def __init__(self, model_name: str, gemini_api_key: str):
        # Use the provided gemini_api_key here for the model init
        self.model = ChatGoogleGenerativeAI(model=model_name, temperature=0, api_key=gemini_api_key)

    def extract_with_schema(self, text: str, schema: str) -> str:
        prompt = f"""
        You are a structured data extractor.

        Extract structured content from the Context below using the schema:

        {schema}

        Context:

        {text}
        """
        response = self.model.invoke(prompt)
        return response.content


class BrightQLAgentScraperTool(BaseTool):
    name: str = Field(default="brightdata_agentql_scraper", description="Tool name")
    description: str = Field(
        default="Extract structured data from a webpage using a schema. Use when given a URL and AgentQL-style schema.",
        description="Tool description"
    )
    bright_token: str
    gemini_token: str

    _bright: BrightDataWebUnlocker = PrivateAttr()
    _extractor: GeminiExtractor = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        bright_token = os.getenv("BRIGHT_DATA_API_TOKEN")
        gemini_token = os.getenv("GEMINI_API_KEY")
        gemini_model = os.getenv("GOOGLE_GEMINI_MODEL_NAME")

        self._bright = BrightDataWebUnlocker(api_token=bright_token)
        self._extractor = GeminiExtractor(gemini_model, gemini_token)

    def _run(self, url: str, is_html: bool, agentql_schema: str) -> str:
        print("Fetching page with Bright Data...")
        if is_html:
            html = self._bright.fetch_html(url)
            print("Parsing with Gemini...")
            return self._extractor.extract_with_schema(html, agentql_schema)
        else:
            markdown = self._bright.fetch_markdown(url)
            print("Parsing with Gemini...")
            return self._extractor.extract_with_schema(markdown, agentql_schema)

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not implemented")
