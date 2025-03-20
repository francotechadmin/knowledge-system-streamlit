import streamlit as st
import autogen
import os
from knowledge_base import KnowledgeBase
from conversation_ui import conversation_ui
from query_ui import query_ui
from knowledge_stats import knowledge_base_stats

# Configuration
if not os.path.exists("OAI_CONFIG_LIST"):
    with open("OAI_CONFIG_LIST", "w") as f:
        f.write('''[
  {
    "model": "gpt-4o",
    "api_key": "YOUR_API_KEY_HERE"
  }
]''')
    st.warning("Created OAI_CONFIG_LIST file. Please add your API key to it and restart the app.")

config_list = autogen.config_list_from_json("OAI_CONFIG_LIST")
llm_config = {
    "config_list": config_list,
}


# Initialize Knowledge Base
kb = KnowledgeBase()

# Main app
def main():

    # Set up Streamlit page
    st.set_page_config(page_title="Knowledge Management System", layout="wide")
    
    st.title("Knowledge Management System")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Conversation", "Query", "Knowledge Base"])
    
    if page == "Conversation":
        conversation_ui(kb, llm_config)
    elif page == "Query":
        query_ui(kb, llm_config)
    elif page == "Knowledge Base":
        knowledge_base_stats(kb)

if __name__ == "__main__":
    main()