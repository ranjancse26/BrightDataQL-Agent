import os
import sys
import asyncio
import logfire

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import set_tracer_provider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
import nest_asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.settings import ModelSettings

nest_asyncio.apply()
load_dotenv()

logfire.configure(
    pydantic_plugin=logfire.PydanticPlugin(record="all"),
    token=os.environ["LOGFIRE_TOKEN"],
)
logfire.instrument_pydantic()
logfire.instrument_httpx(capture_all=True)

exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(exporter)
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(span_processor)

set_tracer_provider(tracer_provider)
Agent.instrument_all()

REQUEST_TIMEOUT = 10000

async def run_agent(query: str) -> str:
    with logfire.span("Within run_agent"):
        brightdata_server = MCPServerStdio(
            command="npx",
            args=["@brightdata/mcp"],
            env={
                "API_TOKEN": os.getenv("BRIGHT_DATA_API_TOKEN"),
                "WEB_UNLOCKER_ZONE": os.getenv("WEB_UNLOCKER_ZONE"),
                "BROWSER_AUTH": os.getenv("BROWSER_AUTH", ""),
            },
        )

        agent = Agent(
            model=os.getenv("GOOGLE_GEMINI_MODEL_NAME"),
            mcp_servers=[brightdata_server],
            retries=3,
            model_settings=ModelSettings(request_timeout=REQUEST_TIMEOUT),
        )

        try:
            async with agent.run_mcp_servers():
                result = await agent.run(query)
                return result.output
        except Exception as e:
            logfire.exception("Agent execution failed", error=str(e))
            return f"Error occurred: {str(e)}"


# Define multiple prompt templates
prompt_templates = {
    "Real Estate": """
You are a real estate property data extractor.

You will be given an url https://www.zillow.com/homes/for_sale/San-Francisco_rb/ of a real estate search results page (e.g., Zillow, Redfin, Realtor.com). These websites often use React-based rendering and do not associate labels and input fields clearly.

Your mission is to extract structured listing data using the schema below. Do **not rely solely on CSS selectors**. If standard element-based targeting fails, fallback to:

- XPath expressions
- Nearby text-based anchors
- Semantic matching of content blocks

You should **not stop** if perfect structure is not found—try alternate methods (including inferred DOM structure or visual position). Use approximate matches and explain where assumptions were made.

Do not depend on labels being directly linked to inputs.

### Sample HTML context:
- Listings are inside cards or tiles
- Prices, bedrooms, and area are shown visibly
- Agent/contact info may be in a footer or modal

---
### SCHEMA:
listings 
    - price
    - address
    - bedrooms
    - bathrooms
    - area_sqft
    - status
    - days_on_market
listing_agent
    - name
    - phone
    - agency
  property_url
  price_history
    - date
    - event
    - price
---

Your response should be ONLY the extracted data in JSON format.

Ignore boilerplate HTML like header, navbar, cookie notices, etc.

If some fields like price history or phone numbers are not found, use `"n/a"`.

Output only in JSON format.
""",
    "Ecommerce Product Extraction": """
Given a product URL https://www.amazon.in/dp/B0D4LWYWF9 make use of the suitable tools for the extraction of the following fields:

product {
- product_title
- price
- rating
- number_of_reviews
- key_features[]
- product_description
- availability
}
""",
    "Job Listings": """
Extract the jobs from https://www.linkedin.com/jobs/linkedin-jobs-bengaluru. Make use of the suitable tools for the data extraction.

Extract the following:
[
- job_title
- company_name
- location
- salary (if available)
- employment_type
- job_description
- job_url
]

Return results in structured JSON. If data is not available, use `"n/a"`.
""",
    "Financial Agent Demo": """
        Extract the stock info from https://finance.yahoo.com/quote/AAPL Make use of the suitable tools for the data extraction. 
        Your mission is to extract structured listing data using the schema below. Do **not rely solely on CSS selectors**. If standard element-based targeting fails, fallback to:

        - XPath expressions
        - Nearby text-based anchors
        - Semantic matching of content blocks

        These pages may be deeply nested, have interactive elements, and may not use well-formed labels or semantic markup.

        Use a robust approach:
        - Prefer **XPath** over CSS selectors.
        - Extract text by **semantic meaning**, visual proximity, and patterns.
        - Do not depend on form labels or attributes.
        - Use "n/a" for missing values.
        - Be strict with format and match the schema exactly.

        Schema
        
        {
            "company": {
                "name": "string",
                "ticker": "string",
                "exchange": "string (e.g., NASDAQ, NYSE)"
            },
            "stock_quote": {
                "price": "float",
                "change": "float",
                "change_percent": "string",
                "last_updated": "string (e.g., 2024-10-01T15:30:00Z)"
            },
            "key_metrics": {
                "market_cap": "string",
                "pe_ratio": "float",
                "eps": "float",
                "dividend_yield": "string",
                "52_week_range": "string"
            },
            "analyst_rating": {
                "consensus": "string (e.g., Buy, Hold, Sell)",
                "price_target_high": "float",
                "price_target_low": "float",
                "price_target_avg": "float"
            },
            "recent_earnings": [
                {
                "quarter": "string (e.g., Q2 2024)",
                "date": "YYYY-MM-DD",
                "actual_eps": "float",
                "expected_eps": "float",
                "revenue": "string"
                }
            ]
        }
""",
}

# Streamlit UI
st.title("BrightDataQL AI Agent")

# Prompt selection dropdown
selected_prompt = st.selectbox(
    "Choose a prompt template", list(prompt_templates.keys())
)
query = st.text_area(
    "Prompt", value=prompt_templates[selected_prompt].strip(), height=350
)

# Run button
run = st.button("Run")

if run and query:
    logfire.info("User triggered Run", query_preview=query)
    with st.spinner("Running MCP agent..."):
        try:
            content = asyncio.run(run_agent(query))
            st.subheader("Answer")
            st.write(content)
        except Exception as e:
            logfire.exception("Error during Streamlit run", error=str(e))
            st.error(f"Error occurred: {e}")
