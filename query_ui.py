import streamlit as st
import autogen
import json
from knowledge_base import KnowledgeBase

# Query interface
def query_ui(kb: KnowledgeBase, llm_config):
    """"
    Interface for querying the knowledge base.
    """
    
    st.header("Query Knowledge Base")
    
    # Get query from user
    query = st.text_input("Enter your query:")
    
    if st.button("Submit Query"):
        if not query:
            st.warning("Please enter a query.")
            return
        
        # Get relevant information from the knowledge base
        with st.spinner("Processing query..."):
            # Analyze the query to determine what information to retrieve
            analysis_agent = autogen.AssistantAgent(
                name="query_analyzer",
                llm_config=llm_config,
                system_message=(
                    "You analyze user queries to determine what information to retrieve from a knowledge base."
                    " For a given query, identify: 1) specific concepts to look up, 2) relationships to find,"
                    " or 3) attributes to search for."
                )
            )
            
            analysis_proxy = autogen.UserProxyAgent(
                name="analysis_proxy",
                human_input_mode="NEVER",
            )
            
            analysis_proxy.initiate_chat(
                analysis_agent,
                message=f"Analyze this query: '{query}'. What information should I retrieve from the knowledge base?",
                max_turns=1
            )
            
            # Get relevant information from the knowledge base
            retrieved_info = {
                "concepts": {},
                "relationships": []
            }
            
            # Extract concepts mentioned in the query
            for concept in kb.data["concepts"].keys():
                if concept.lower() in query.lower():
                    retrieved_info["concepts"][concept] = kb.query_concept(concept)
                    # Get relationships for this concept
                    retrieved_info["relationships"].extend(kb.query_relationships(concept))
            
            # If no specific concepts found, provide a summary
            if not retrieved_info["concepts"]:
                concept_count = len(kb.data["concepts"])
                relationship_count = len(kb.data["relationships"])
                retrieved_info["summary"] = f"Knowledge base contains {concept_count} concepts and {relationship_count} relationships."
                # Include a sample of concepts
                sample_size = min(5, concept_count)
                retrieved_info["sample_concepts"] = list(kb.data["concepts"].keys())[:sample_size]
            
            # Now answer the query with the retrieved information
            info_json = json.dumps(retrieved_info, indent=2)
            
            # Create the query assistant
            query_assistant = autogen.AssistantAgent(
                name="query_assistant",
                llm_config=llm_config,
                system_message=(
                    "You are an assistant that helps users query a knowledge base."
                    " You have access to information about concepts and their relationships."
                    " When responding to queries, use only the information provided by the knowledge base."
                )
            )
            
            query_proxy = autogen.UserProxyAgent(
                name="query_proxy",
                human_input_mode="NEVER",
            )
            
            query_proxy.initiate_chat(
                query_assistant,
                message=(
                    f"Based on the following information from our knowledge base, please answer this query: '{query}'\n\n"
                    f"Retrieved information: {info_json}"
                ),
                max_turns=1
            )
            
            response = query_assistant.last_message()["content"]
        
        # Display the response
        st.subheader("Answer")
        st.write(response)
        
        # Display the retrieved information
        with st.expander("Retrieved Information"):
            st.json(retrieved_info)
