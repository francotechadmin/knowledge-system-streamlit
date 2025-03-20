import json
import os
from typing import Dict, List, Optional
import autogen
import streamlit as st
from knowledge_base import KnowledgeBase


# Function to extract knowledge from conversation
def extract_knowledge(conversation_text: str, llm_config: Dict) -> Dict:
    """
    Extract knowledge from conversation text using an LLM.
    Returns a dictionary with concepts and relationships.
    """
    extraction_agent = autogen.AssistantAgent(
        name="knowledge_extractor",
        llm_config=llm_config,
        system_message=(
            "You are an expert knowledge extraction system. Your task is to analyze the"
            " conversation and extract key concepts, their attributes, and relationships between them."
            " Format your response as a JSON object with two main keys:"
            " 'concepts' (a dictionary of concept names to their attributes) and"
            " 'relationships' (a list of source-relation-target triples)."
        ),
        codeExecutionConfig={"use_docker": False}
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config={"work_dir": "knowledge_extraction"},
        codeExecutionConfig={"use_docker": False},
    )
    
    user_proxy.initiate_chat(
        extraction_agent, 
        message=(
            f"Please extract structured knowledge from the following conversation:"
            f"\n\n{conversation_text}\n\n"
            f"Return only the JSON object with the extracted knowledge."
        ),
        max_turns=1
    )
    
    # Get the last message from the extraction agent
    last_message = extraction_agent.last_message().get("content", "")
    
    # Extract the JSON part from the message
    try:
        # Try to find JSON between triple backticks
        import re
        json_match = re.search(r"```json\n(.*?)\n```", last_message, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # If not found, try to extract any JSON-like structure
            start_idx = last_message.find("{")
            end_idx = last_message.rfind("}")
            if start_idx != -1 and end_idx != -1:
                json_str = last_message[start_idx:end_idx+1]
            else:
                return {"concepts": {}, "relationships": []}
        
        return json.loads(json_str)
    except json.JSONDecodeError:
        st.error("Error parsing JSON from extraction agent")
        return {"concepts": {}, "relationships": []}

# Function to update the knowledge base with extraction results
def update_knowledge_base(extraction_result: Dict, kb: KnowledgeBase):
    """Update the knowledge base with new extraction results"""
    # Add concepts
    for concept_name, attributes in extraction_result.get("concepts", {}).items():
        kb.add_concept(concept_name, attributes)
    
    # Add relationships
    for rel in extraction_result.get("relationships", []):
        if all(k in rel for k in ["source", "relation", "target"]):
            kb.add_relationship(rel["source"], rel["relation"], rel["target"])
