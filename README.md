# BrightDataQL-Agent
Introducing the State-of-the-Art Bright Data MCP Agent - A next-generation web data intelligence system powered by Bright Data’s Model Context Protocol (MCP) and BrightDataQL (Bright Data Query Language), a schema-first, declarative query interface for extracting structured information.

The agent doesn't just "browse" or "scrape" the web. It discovers, navigates, interacts, and extracts high-value information from complex, protected, or JavaScript-heavy web environments just like a human would and transforms it into structured, machine-consumable output via a natural language interface.

# Pre-Requisite

- Signup on https://brightdata.com/
- Create the following proxies for Web Unlocker, SERP, Scraping Browser and MCP Server
![BrightData-Proxies](https://github.com/user-attachments/assets/bc62a6a9-f9bf-4859-8741-34e509735f20)
- Copy the API Keys for each of them
- Optional Logfire - https://pydantic.dev/logfire
- Google Gemini API Key. You may obtain from https://aistudio.google.com/

# Replace the .env

Please replace the following .env with your secret keys

- BRIGHT_DATA_API_TOKEN=
- WEB_UNLOCKER_ZONE=mcp_unlocker
- BROWSER_AUTH=
- GEMINI_API_KEY=
- GOOGLE_GEMINI_MODEL_NAME=gemini-2.0-flash
- MAX_MCP_AGENT_STEPS=5
- LOGFIRE_TOKEN=<optional>
- LOGFIRE_IGNORE_NO_CONFIG=1

# Demo

**Real-estate use-case**

![Real-estate-demo](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7kqx1s5cq9rwqhokhxwk.png)

**Amazon Scrapping Browser Demo**

![Amazon-Scrapping-Browser](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/f7cblfhu6xdexe2j3wl8.png)

## Behind the scenes

```
Thought: I need to execute the steps in the provided BEGIN...END block. First, I will navigate to the Amazon website. Then, I will type "wireless earbuds" into the search bar and submit the search. After waiting for the search results to load, I will click on the first search result. Finally, I will extract the title, price, and description of the product and return them in a JSON format.

Action: scraping_browser_navigate
Action Input: {"url": "https://www.amazon.com"}
Observation: {'status': 'OK'}
Thought: Now I need to type "wireless earbuds" into the search bar.
Action: scraping_browser_type
Action Input: {"selector": "input[name='field-keywords']", "text": "wireless earbuds"}
Observation: {'status': 'OK'}
Thought: Now I need to click the submit button to start the search.
Action: scraping_browser_click
Action Input: {"selector": "input[type='submit']"}
Observation: {'status': 'OK'}
Thought: Now I need to wait for the search results to load.
Action: scraping_browser_wait_for
Action Input: {"selector": "div[data-component-type='s-search-result']"}
Observation: {'status': 'OK'}
Thought: Now I need to click on the first search result.
Action: scraping_browser_click
Action Input: {"selector": "div[data-component-type='s-search-result'] a.a-link-normal"}
Observation: {'status': 'OK'}
Thought: Now I need to wait for the product page to load.
Action: scraping_browser_wait_for
Action Input: {"selector": "#productTitle"}
Observation: {'status': 'OK'}
Thought: Now I need to get the product title.
Action: scraping_browser_get_text
Action Input: {"selector": "#productTitle"}
Observation: {'status': 'OK', 'text': 'TOZO T6 True Wireless Earbuds Bluetooth 5.3 Headphones Wireless Earphones IPX8 Waterproof Stereo Sound 
Headsets with Wireless Charging Case Black'}
Thought: Now I need to get the product price.
Action: scraping_browser_get_text
Action Input: {"selector": ".a-price .a-offscreen"}
Observation: {'status': 'OK', 'text': '$25.49'}
Thought: Now I need to get the product description.
Action: scraping_browser_get_text
Action Input: {"selector": "#feature-bullets"}
Observation: {'status': 'OK', 'text': '[\n    "\\ud83d\\udca8[Hi-Fi Stereo Sound Quality]: TOZO T6 Offers a truly authentic sound and powerful bass performance with 10 mm large size speaker driver - the drive area is 1.77 times than the normal drive area.",\n    "\\ud83d\\udca8[Bluetooth 5.3 Technology]: Adopt the advanced Bluetooth 5.3 technology. TOZO T6 Support HSP, HFP, A2DP, AVRCP, which greatly improve the transmission speed and providing you with a low-latency listening experience.",\n    "\\ud83d\\udca8[One step pairing]: Pick up 2 Headsets from Charging box They will connect each other automatically, then only one step easily enter mobile phone Bluetooth setting to pair the earbuds.",\n    "\\ud83d\\udca8[IPX8 Waterproof]: Earbuds and charging case inner Nano-coating makes it possible to waterproof for 1 meters deep for 30 minutes. Waterproof and sweatproof latest technology can effectively prevent from the damage of the splash by sweat and raindrops.",\n    "\\ud83d\\udca8[Charge on the go]: TOZO T6 wireless earbuds can last for over 6 hours’ playtime from a single charge and 30 extra hours in the compact charging case. Charging case support wireless charging and Type-C charging. Providing convenient charging way with no strings attached."\n]'}    
Thought: I have successfully extracted the title, price, and description of the product. Now I need to return them in a JSON format.
Final Answer: {"title": "TOZO T6 True Wireless Earbuds Bluetooth 5.3 Headphones Wireless Earphones IPX8 Waterproof Stereo Sound Headsets with 
Wireless Charging Case Black", "price": "$25.49", "description": "[\n    \"\\ud83d\\udca8[Hi-Fi Stereo Sound Quality]: TOZO T6 Offers a truly 
authentic sound and powerful bass performance with 10 mm large size speaker driver - the drive area is 1.77 times than the normal drive area.\",\n    \"\\ud83d\\udca8[Bluetooth 5.3 Technology]: Adopt the advanced Bluetooth 5.3 technology. TOZO T6 Support HSP, HFP, A2DP, AVRCP, which 
greatly improve the transmission speed and providing you with a low-latency listening experience.\",\n    \"\\ud83d\\udca8[One step pairing]: 
Pick up 2 Headsets from Charging box They will connect each other automatically, then only one step easily enter mobile phone Bluetooth setting to pair the earbuds.\",\n    \"\\ud83d\\udca8[IPX8 Waterproof]: Earbuds and charging case inner Nano-coating makes it possible to waterproof for 1 meters deep for 30 minutes. Waterproof and sweatproof latest technology can effectively prevent from the damage of the splash by sweat 
and raindrops.\",\n    \"\\ud83d\\udca8[Charge on the go]: TOZO T6 wireless earbuds can last for over 6 hours’ playtime from a single charge and 30 extra hours in the compact charging case. Charging case support wireless charging and Type-C charging. Providing convenient charging way with no strings attached.\"\n]"}
```
