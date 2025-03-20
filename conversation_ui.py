import streamlit as st
import autogen
import time
from knowledge_base import KnowledgeBase
from utils import extract_knowledge, update_knowledge_base

# Conversation Manager
def conversation_ui(kb: KnowledgeBase, llm_config):
    """"
    Interface for managing knowledge extraction conversations.
    """

    st.header("Knowledge Extraction Conversation")

    # Create the assistant agent
    assistant = autogen.AssistantAgent(
        name="domain_expert_interface",
        llm_config=llm_config,
        system_message=(
            "You are an interface to communicate with domain experts. Your goal is to"
            " ask relevant questions to extract their knowledge about a specific domain."
            " Ask one question at a time, focusing on technical details, processes,"
            " relationships between concepts, and key attributes."
        )
    )
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        
    )

    auto_reply_agent = autogen.AssistantAgent(
        name="auto_reply_agent",
        llm_config=llm_config,
        system_message=(
            "You are an assistant that acts as a user to reply to the assistant agent."
            " Your goal is to provide relevant responses to the assistant's questions."
        )
    )
    
    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Get domain from user if not already set
    if "domain" not in st.session_state:
        domain = st.text_input("Enter the domain/topic for the conversation:")
        if domain:
            st.session_state.domain = domain
            # Add initial message from assistant
            initial_message = f"I'd like to learn about your expertise in {domain}. What are the key concepts in this domain?"
            st.session_state.messages.append({"role": "assistant", "content": initial_message})
            st.rerun()  # Rerun to update UI
        else:
            st.info("Please enter a domain to start the conversation.")
            return
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Accept user input
    if prompt := st.chat_input("Your response (type 'end' to finish the conversation)"):
        # if not prompt, use an agent to generate a response
        if not prompt or prompt.strip() == "auto":
            # Generate a response using the auto_reply_agent
            with st.spinner("Generating response..."):
                auto_reply_agent.run(f"Respond to the assistant's last message: {st.session_state.messages[-1]['content']}", max_turns=1)
                prompt = auto_reply_agent.last_message()["content"]

            if not prompt:
                st.warning("No response generated. Please try again.")
                return
   
        # Check if user wants to end the conversation
        if prompt.lower() == "end":
            st.success("Conversation ended. Extracting knowledge...")
            
            # Get the conversation text
            conversation_text = "\n".join([m["content"] for m in st.session_state.messages])
            
            # Extract knowledge
            with st.spinner("Extracting knowledge from the conversation..."):
                extraction_result = extract_knowledge(conversation_text, llm_config)
            
            # Update knowledge base
            update_knowledge_base(extraction_result, kb)
            
            # Show extraction results
            st.subheader("Extracted Knowledge")
            
            # Display concepts
            st.write(f"Extracted {len(extraction_result.get('concepts', {}))} concepts:")
            for concept, attributes in extraction_result.get("concepts", {}).items():
                with st.expander(f"Concept: {concept}"):
                    st.json(attributes)
            
            # Display relationships
            st.write(f"Extracted {len(extraction_result.get('relationships', []))} relationships:")
            for rel in extraction_result.get("relationships", []):
                if all(k in rel for k in ["source", "relation", "target"]):
                    st.write(f"- {rel['source']} {rel['relation']} {rel['target']}")
            
            # Reset conversation for next time
            if st.button("Start New Conversation"):
                st.session_state.messages = []
                st.session_state.domain = None
                st.rerun()
            
            return
                
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate assistant response - use a container to show real-time updates
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            

            # Get response
            with st.spinner("Assistant is thinking..."):
                user_proxy.initiate_chat(
                    assistant,
                    message=prompt,
                    max_turns=1
                )
                
                response = assistant.last_message()["content"]
            
            # Simulate streaming for a more interactive feel
            for word in response.split():
                full_response += word + " "
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)
                
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
            
        # Force a rerun to properly display the updated chat
        st.rerun()
