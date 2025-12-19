import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI
import os
import json
# Load API key from config.json
def load_api_key():
    with open("openai_api.json", "r") as file:
        config = json.load(file)
    return config["API_KEY"]

api_key = load_api_key()


# Initialize the OpenAI client
client = OpenAI(api_key=api_key)


def extract_text_from_pdfs(uploaded_files):
    """Extract and combine text from multiple uploaded PDF files."""
    combined_text = ""
    for uploaded_file in uploaded_files:
        try:
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    combined_text += page.get_text()
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {e}")
    return combined_text

def generate_aggregate_metadata(combined_text, bot_type):
    """
    Generate aggregate metadata for a bot based on combined document text.
    :param combined_text: Combined text from all relevant documents.
    :param bot_type: The bot type for which metadata is being generated.
    :return: A dictionary containing aggregated metadata for Capabilities, Description, and Specialization Keywords.
    """
    # Define prompts for metadata fields
    prompts = {
        "Capabilities": f"Based on the following combined document text, list the specific capabilities that a {bot_type} should have:\n\n{combined_text}\n\nCapabilities:",
        "Description": f"Summarize the purpose and scope of the following combined documents as they relate to a {bot_type}:\n\n{combined_text}\n\nDescription:",
        "Specialization Keywords": f"Extract a list of comma-separated keywords that describe the capabilities, functions, and information this bot can provide based on the following document text:\n\n{combined_text}\n\nSpecialization Keywords (comma-separated):"
    }



    # Dictionary to store metadata results
    metadata = {}

    # Call the LLM for each metadata field
    for field, prompt in prompts.items():
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            metadata[field] = response.choices[0].message.content.strip()
        except Exception as e:
            st.error(f"Error generating {field} for {bot_type}: {e}")
            metadata[field] = "Error generating this field."

    return metadata

def main():
    st.title("Bot Metadata Generator")

    st.sidebar.header("Upload PDF Files")
    uploaded_files = st.sidebar.file_uploader(
        "Choose PDF files", type="pdf", accept_multiple_files=True
    )

    st.sidebar.header("Bot Configuration")
    bot_options = ["Customer Database Bot", "Organizational Information Bot", "Internet Search Bot", "Custom Bot"]
    bot_type = st.sidebar.selectbox("Select Bot Type", bot_options)

    if bot_type == "Custom Bot":
        bot_type = st.sidebar.text_input("Enter Custom Bot Name")

    if st.sidebar.button("Generate Metadata"):
        if not uploaded_files:
            st.error("Please upload at least one PDF file.")
        elif not bot_type:
            st.error("Please specify a bot name.")
        else:
            with st.spinner("Processing..."):
                combined_text = extract_text_from_pdfs(uploaded_files)
                if combined_text:
                    metadata = generate_aggregate_metadata(combined_text, bot_type)
                    st.success("Metadata generated successfully!")
                    st.json(metadata)
                    # Convert metadata to JSON string for download
                    metadata_json = json.dumps(metadata, indent=4)
                    st.download_button(
                        label="Download Metadata",
                        data=metadata_json,
                        file_name=f"{bot_type.replace(' ', '_')}_metadata.json",
                        mime="application/json"
                    )
                else:
                    st.error("No text could be extracted from the uploaded PDFs.")

if __name__ == "__main__":
    main()