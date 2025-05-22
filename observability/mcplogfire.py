import os
import logfire

def init():
    token = os.environ["LOGFIRE_TOKEN"]
    if token != "":
        logfire.configure(pydantic_plugin=logfire.PydanticPlugin(record='all'),
            token=token)
        #logfire.instrument_pydantic()
        logfire.instrument_httpx(capture_all=True)