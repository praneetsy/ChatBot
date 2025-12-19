import fitz  # PyMuPDF
from langchain_openai import ChatOpenAI
from database.vector_store import ChromaDBVectorStore
from langchain_core.messages import HumanMessage, SystemMessage


class MetadataExtractor:
    def __init__(self, model="qwen2.5-coder-7b-instruct"):
        self.client = ChatOpenAI(
            model=model,
            max_tokens=1024,
            temperature=0.4, # We set the temperature to 0.4 to ensure the generated text is more coherent and has added variety.
            model_kwargs={
                "response_format": "json_schema",
            },
        )
        # Define the JSON schema for the structured output for metadata extraction
        json_schema = {
            "title": "Metadata Extraction",
            "description": "Schema for extracting metadata from a document.",
            "type": "object",
            "properties": {
                "capabilities": {
                    "type": "string",
                },
                "description": {
                    "type": "string",
                },
                "keywords": {
                    "type": "string",
                },
            },
            "additionalProperties": False,
        }
        self.llm = self.client.with_structured_output(json_schema, method="json_schema")
        self.vector_store = ChromaDBVectorStore("database/chromadb")

    def extract_text_from_pdf(self, pdf_path):
        """Extract and combine text from a single PDF file."""
        combined_text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    combined_text += page.get_text()
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return combined_text

    def generate_llm_based_metadata(self, text, agent_name):
        """
        Generate aggregate metadata for a bot based on combined document text.
        :param combined_text: Combined text from all relevant documents.
        :param bot_type: The bot type for which metadata is being generated (e.g., "Customer Database Bot").
        :return: A dictionary containing aggregated metadata for Capabilities, Description, and Keywords.
        """
        # Define prompts for metadata fields
        text_prompt = f"Document Text:\n{text}\n\n"

        # Dictionary to store metadata results
        metadata = {}

        try:
            system_message = SystemMessage(
                content=f"""
                You are a helpful assistant. You can judge based on the document text and agent, what is the stuff can the agent answer. 
                Based on the following combined document text, provide the following information for a {agent_name}:
                1. List the specific capabilities that the agent should have.
                2. Summarize the purpose and scope of the documents as they relate to the agent.
                3. Extract key phrases and terms that would help identify them as related to the agent.
                Keep it under 1000 words
                """
            )
            human_message = HumanMessage(content=text_prompt)
            response = self.llm.invoke([system_message, human_message])
            response_content = response
            print(response_content)
            metadata["capabilities"] = response_content[
                "capabilities"
            ]  # These are the capabilities that are introduced by the document for the agent.
            metadata["description"] = response_content[
                "description"
            ]  # This is the description of the document.
            metadata["keywords"] = response_content[
                "keywords"
            ]  # These are the keywords that are introduced by the document for the agent.
        except Exception as e:
            print(f"Error generating metadata for {agent_name}: {e}")
            raise e

        return metadata

    def save_metadata(self, metadata, agent_name, filename):
        self.vector_store.add_agent_metadata(
            agent_name=agent_name, metadata=metadata, filename=filename
        )

    def extract_and_save_metadata_from_text(
        self, text, agent_name, filename="manual_text"
    ):
        metadata = self.generate_llm_based_metadata(text, agent_name)
        self.save_metadata(metadata, agent_name, filename)
