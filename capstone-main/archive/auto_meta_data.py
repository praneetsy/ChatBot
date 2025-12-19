import fitz  # PyMuPDF
import openai
import os

# Set your OpenAI API key
#openai.api_key = os.getenv("sk-LFLTGyz5_itvflWN2_LKiohf-sJqfeATunE41XBdSkT3BlbkFJadyQ-XkMdcbWbsiFPk0G1jDnS11NZRks9axm6BR7kA")  # Ensure your API key is set in the environment
import json
import fitz  # PyMuPDF
from openai import OpenAI
import os

def load_api_key():
    with open("openai_api.json", "r") as file:
        config = json.load(file)
    return config["API_KEY"]

api_key = load_api_key()
# Initialize the OpenAI client
client = OpenAI(api_key=api_key)


def extract_text_from_pdfs(pdf_paths):
    """Extract and combine text from multiple PDF files."""
    combined_text = ""
    for pdf_path in pdf_paths:
        try:
            with fitz.open(pdf_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    combined_text += page.get_text()
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
    return combined_text

def generate_aggregate_metadata(combined_text, bot_type):
    """
    Generate aggregate metadata for a bot based on combined document text.
    :param combined_text: Combined text from all relevant documents.
    :param bot_type: The bot type for which metadata is being generated (e.g., "Customer Database Bot").
    :return: A dictionary containing aggregated metadata for Capabilities, Description, and Specialization Keywords.
    """
    # Define prompts for metadata fields
    prompts = {
        "Capabilities": f"Based on the following combined document text, list the specific capabilities"
                        f" that a {bot_type} should have:\n\n{combined_text}\n\nCapabilities:",
        "Description": f"Summarize the purpose and scope of the following combined documents "
                       f"as they relate to a {bot_type}:\n\n{combined_text}\n\nDescription:",
        "Specialization Keywords": f"Extract key phrases and terms from the following combined documents "
                                   f"that would help identify them as related to a {bot_type}:\n\n{combined_text}\n\nSpecialization Keywords:"
    }
    """
    prompts = {
        "Capabilities": f"Based on the following combined document text, list the specific capabilities"
                        f" that a {bot_type} should have. Capabilities:",
        "Description": f"Summarize the purpose and scope of the following combined documents "
                       f"as they relate to a {bot_type}.Description:",
        "Specialization Keywords": f"Extract key phrases and terms from the following combined documents "
                                   f"that would help identify them as related to a {bot_type}."
                                   f"Specialization Keywords:"
    }
"""
    # Dictionary to store metadata results
    metadata = {}

    # Call the LLM for each metadata field
    for field, prompt in prompts.items():
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            metadata[field] = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating {field} for {bot_type}: {e}")
            metadata[field] = "Error generating this field."

    return metadata

def process_documents(pdf_paths, bot_type="Customer Database Bot",output_file="metadata.json"):
    """
    Process multiple PDFs, extract text, and generate aggregate metadata.
    :param pdf_paths: List of PDF file paths.
    :param bot_type: Type of bot for which metadata is being generated.
    :return: Dictionary of aggregated metadata for the bot.
    """
    # Extract and combine text from all PDFs
    combined_text = extract_text_from_pdfs(pdf_paths)
    if not combined_text:
        print("No text extracted from the provided PDFs.")
        return {}

    # Generate aggregate metadata using the LLM
    aggregate_metadata = generate_aggregate_metadata(combined_text, bot_type)
    # Save the metadata to a JSON file
    try:
        with open(output_file, 'w') as file:
            json.dump(aggregate_metadata, file, indent=4)
        print(f"Metadata successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving metadata to {output_file}: {e}")

    return aggregate_metadata



# Example usage
if __name__ == "__main__":
    pdf_files = ["documents/employee_benefits.pdf", "documents/org_structure.pdf"]
    bot_type = "Customer Database Bot"  # Adjust based on bot type
    output_file = "customer_database_bot_metadata.json"
    metadata_results = process_documents(pdf_files, bot_type=bot_type,output_file = output_file)

    # Print results for each document
    print(f"\nAggregated Metadata for {bot_type}:")
    for key, value in metadata_results.items():
        print(f"{key}: {value}")
