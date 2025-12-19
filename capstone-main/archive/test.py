# %%
import requests
from langchain.embeddings.base import Embeddings
from typing import List


# Define a class that uses the HTTP API to get embeddings
class HTTPEmbeddingModel(Embeddings):
    def __init__(self, api_url: str, model_name: str):
        """
        Initialize with the base URL of the HTTP server and model name.
        
        :param api_url: The API endpoint that returns the embeddings.
        :param model_name: The model to use when making the request.
        """
        self.api_url = api_url
        self.model_name = model_name
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding for a single piece of text by making an HTTP request.
        
        :param text: The text to get embeddings for.
        :return: A list of floats representing the embedding.
        """
        payload = {
            "model": self.model_name,
            "input": text
        }

        response = requests.post(self.api_url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            raise ValueError(f"Error getting embedding: {response.text}")
        
        response_json = response.json()

        # Extract the first embedding from the "data" field
        embedding_data = response_json.get("data", [])
        if len(embedding_data) == 0:
            raise ValueError("No embeddings found in the response.")

        # Assuming we are interested in the first embedding returned
        return embedding_data[0].get("embedding", [])
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents (texts).
        
        :param texts: List of documents to embed.
        :return: A list of lists, where each inner list is an embedding.
        """
        embeddings = []
        for text in texts:
            embedding = self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query (text).
        
        :param text: The query text to embed.
        :return: A list of floats representing the embedding.
        """
        return self.get_embedding(text)

# %%
from langchain_community.vectorstores import SQLiteVSS


# %%
import sqlite3 as sqllite3
api_url = "http://127.0.0.1:1234/v1/embeddings"

model_name = "nomic-embed-text-v1.5"
embd = HTTPEmbeddingModel(api_url=api_url, model_name=model_name)
conn = SQLiteVSS.create_connection("sqllite.db")
vss = SQLiteVSS(connection=conn, embedding=embd, table="agents")
vss.similarity_search("Hello", 5)



# %%



