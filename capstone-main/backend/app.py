from typing import Union
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from agent.triage import TriageAgent
from documents.metadata import MetadataExtractor
load_dotenv()


# This configuration uses LM Studio to run the LLMs locally - replace 
# with your own OpenAI API key and base URL if you are using the API.
# Make sure you use an .env file to store your API key and base URL instead of 
# hardcoding them here.
os.environ['OPENAI_BASE_URL'] = os.getenv('OPENAI_BASE_URL', "http://host.docker.internal:1234/v1")
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', "test")
app = FastAPI(
    middleware=[
         Middleware(CORSMiddleware, allow_origins=["*"])
    ]
)

@app.get("/")
def read_root():
    return {"Hello": "World"}


# API Call to get text from user and extract metadata to save it for a specific agent name
@app.post("/metadata")
def extract_metadata(agent_name: str, text: str):
    """
    Extracts metadata from the provided text and saves it using the specified agent name.

    Args:
        agent_name (str): The name of the agent performing the metadata extraction.
        text (str): The text from which metadata needs to be extracted.

    Returns:
        dict: A dictionary containing the status of the operation.
            Example: {"status": "success"}

    Comments for frontend:
        - Endpoint: POST /metadata
        - Request Body: JSON object with 'agent_name' and 'text' fields.
        - Response: JSON object with a 'status' field indicating the success of the operation.
    """
    metadata_extractor = MetadataExtractor()

    metadata_extractor.extract_and_save_metadata_from_text(text, agent_name)
    return {"status": "success"}


# Load the triage agent
triage_agent = TriageAgent()
triage_agent.load_agent()

# API call to get user query and return agents similar to the query
@app.get("/agents")
def get_similar_agents(query: str):
    """
    Endpoint to retrieve similar agents based on a query string.

    Args:
        query (str): The query string to search for similar agents.

    Returns:
        list: A list of agents relevant to the provided query.

    This function retrieves relevant agents based on the query string provided.
    
    Comments for frontend:
        - Endpoint: GET /agents
        - Request Parameters: query
        - Response: JSON object with a list of relevant agents
    """
    res = triage_agent.get_relevant_agents_from_query(query)
    res['conversation_history'] = [msg.content for msg in triage_agent.get_generated_conversation_log()]
    return res