import json
import streamlit as st
from typing import Dict, List, Optional

# Knowledge Base Storage using Streamlit's session_state for browser storage
class KnowledgeBase:
    def __init__(self):
        # Initialize knowledge base in session state if it doesn't exist
        if "knowledge_base" not in st.session_state:
            st.session_state.knowledge_base = {"concepts": {}, "relationships": []}
        self.data = st.session_state.knowledge_base
    
    def save_data(self):
        # Data is already stored in session_state, no need to write to file
        st.session_state.knowledge_base = self.data
    
    def add_concept(self, name: str, attributes: Dict):
        """Add or update a concept in the knowledge base"""
        self.data["concepts"][name] = attributes
        self.save_data()
    
    def add_relationship(self, source: str, relation: str, target: str):
        """Add a relationship between concepts"""
        rel = {"source": source, "relation": relation, "target": target}
        if rel not in self.data["relationships"]:
            self.data["relationships"].append(rel)
            self.save_data()
    
    def query_concept(self, name: str) -> Optional[Dict]:
        """Query information about a specific concept"""
        return self.data["concepts"].get(name)
    
    def query_relationships(self, concept: str) -> List[Dict]:
        """Find all relationships involving a concept"""
        return [
            rel for rel in self.data["relationships"] 
            if rel["source"] == concept or rel["target"] == concept
        ]
    
    def query_by_attribute(self, attribute: str, value: str) -> List[str]:
        """Find concepts that have a specific attribute value"""
        return [
            name for name, attrs in self.data["concepts"].items()
            if attrs.get(attribute) == value
        ]
    
    def export_data(self) -> Dict:
        """Export the knowledge base as a dictionary"""
        return self.data
    
    def import_data(self, data: Dict):
        """Import data into the knowledge base"""
        self.data = data
        self.save_data()