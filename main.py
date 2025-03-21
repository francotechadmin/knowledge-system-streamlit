import streamlit as st
import json
import os
from dotenv import load_dotenv
from knowledge_base import KnowledgeBase
from conversation_ui import conversation_ui
from audio_conversation_ui import audio_conversation_ui
from query_ui import query_ui
from knowledge_stats import knowledge_base_stats

# Load environment variables
load_dotenv()

# Configuration
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.warning("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

config_list = [{"model": "gpt-4o", "api_key": api_key}]
llm_config = {"config_list": config_list}

# Initialize Knowledge Base
kb = KnowledgeBase()

# Add export/import functionality
def export_import_ui():
    st.sidebar.header("Export/Import")
    
    # Export functionality
    if st.sidebar.button("Export Knowledge Base"):
        export_data = kb.export_data()
        st.sidebar.download_button(
            label="Download JSON",
            data=json.dumps(export_data, indent=2),
            file_name="knowledge_base_export.json",
            mime="application/json"
        )
    
    # Import functionality
    uploaded_file = st.sidebar.file_uploader("Import Knowledge Base", type=["json"])
    if uploaded_file is not None:
        try:
            import_data = json.load(uploaded_file)
            if st.sidebar.button("Load Imported Data"):
                kb.import_data(import_data)
                st.sidebar.success("Knowledge base imported successfully!")
        except Exception as e:
            st.sidebar.error(f"Error importing file: {str(e)}")

# Main app
def main():
    # Set up Streamlit page
    st.set_page_config(page_title="Knowledge Management System", layout="wide")
    
    st.title("Knowledge Management System")
    
    # Check for API key
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Show instructions for setting environment variables
        st.markdown("""
        ### How to set up your API key:
        
        #### Option 1: Environment variable
        Set the `OPENAI_API_KEY` environment variable before running the app.
        
        #### Option 2: Create a .env file
        Create a file named `.env` in the same directory as this script with the following content:
        ```
        OPENAI_API_KEY=your_api_key_here
        ```
        """)
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Audio Conversation", "Text Conversation", "Query", "Knowledge Base"])
    
    # Add export/import UI to sidebar
    export_import_ui()
    
    if page == "Text Conversation":
        conversation_ui(kb, llm_config)
    elif page == "Audio Conversation":
        audio_conversation_ui(kb, llm_config)
    elif page == "Query":
        query_ui(kb, llm_config)
    elif page == "Knowledge Base":
        knowledge_base_stats(kb)

if __name__ == "__main__":
    main()