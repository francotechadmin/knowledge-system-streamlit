import streamlit as st
from knowledge_base import KnowledgeBase

# Knowledge base statistics
def knowledge_base_stats(kb: KnowledgeBase):
    """
    Display statistics and contents of the knowledge base.
    """
    
    st.header("Knowledge Base Statistics")
    
    concept_count = len(kb.data["concepts"])
    relationship_count = len(kb.data["relationships"])
    
    st.write(f"Total concepts: {concept_count}")
    st.write(f"Total relationships: {relationship_count}")
    
    if concept_count > 0:
        # Display concepts
        st.subheader("Concepts")
        for concept, attributes in kb.data["concepts"].items():
            with st.expander(f"{concept}"):
                st.json(attributes)
        
        # Display relationships
        st.subheader("Relationships")
        for rel in kb.data["relationships"]:
            st.write(f"- {rel['source']} {rel['relation']} {rel['target']}")
