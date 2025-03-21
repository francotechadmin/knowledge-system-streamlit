import streamlit as st
import os
import time
import openai
from knowledge_base import KnowledgeBase
from utils import extract_knowledge, update_knowledge_base

def audio_conversation_ui(kb: KnowledgeBase, llm_config):
    """
    Interface for a back-and-forth audio conversation between user and bot.
    """
    st.header("Audio Conversation")
    
    # Button to start a new conversation
    if st.button("Start New Conversation") or "messages" not in st.session_state:
        st.session_state.messages = []
        initial_message = "Hello! I'm your AI assistant. What would you like to talk about today?"
        st.session_state.messages.append({"role": "assistant", "content": initial_message})
        
        # Auto-generate and play initial greeting
        speech_file = f"assistant_audio_0.mp3"
        generate_speech(initial_message, speech_file)
        st.session_state.messages[-1]["audio_path"] = speech_file
        st.rerun()
    
    # Button to end conversation and extract knowledge
    if len(st.session_state.messages) > 0 and st.button("End Conversation & Extract Knowledge"):
        end_conversation(kb, llm_config)
        return
    
    # Display conversation with auto-play for new assistant messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # Display audio if available
            if "audio_path" in message and os.path.exists(message["audio_path"]):
                # Auto-play if this is the most recent assistant message
                if message["role"] == "assistant" and i == len(st.session_state.messages) - 1:
                    st.audio(message["audio_path"], autoplay=True)
                else:
                    st.audio(message["audio_path"])
    
    # Audio input with instruction for manual stop
    st.markdown("##### Voice Recording (click 'Stop recording' when done)")
    audio_key = f"audio_input_{len(st.session_state.messages)}"
    audio_bytes = st.audio_input("Record your message", key=audio_key)
        
    # Text input as alternative
    text_key = f"text_input_{len(st.session_state.messages)}"
    text_input = st.text_input("Or type your message", key=text_key)
    text_button = st.button("Send text", key=f"send_{len(st.session_state.messages)}")
    
    # Process audio input
    if audio_bytes is not None:
        process_audio_input(audio_bytes, kb, llm_config)
    
    # Process text input
    if text_button and text_input:
        process_text_input(text_input, kb, llm_config)

def process_audio_input(audio_bytes, kb, llm_config):
    """Process audio input and generate a response"""
    # Save audio to file
    audio_file = f"user_audio_{len(st.session_state.messages)}.wav"
    with open(audio_file, "wb") as f:
        f.write(audio_bytes.getvalue())
    
    # Transcribe audio
    with st.spinner("Transcribing your audio..."):
        transcript = transcribe_audio(audio_file)
        
        if not transcript:
            st.error("Failed to transcribe audio. Please try again.")
            return
    
    # Add user message to conversation
    st.session_state.messages.append({
        "role": "user",
        "content": transcript,
        "audio_path": audio_file
    })
    
    # Generate assistant response
    generate_response(transcript, kb, llm_config)
    
    # Rerun to update UI
    st.rerun()

def process_text_input(text, kb, llm_config):
    """Process text input and generate a response"""
    # Add user message to conversation
    st.session_state.messages.append({
        "role": "user",
        "content": text
    })
    
    # Generate assistant response
    generate_response(text, kb, llm_config)
    
    # Rerun to update UI
    st.rerun()

def generate_response(user_input, kb, llm_config):
    """Generate a response from the assistant"""
    # Create message list for the API
    messages = [
        {"role": "system", "content": """
            You are an interface to communicate with domain experts. Your goal is to
            ask relevant questions to extract their knowledge about a specific domain.
            Ask one question at a time, focusing on technical details, processes,
            relationships between concepts, and key attributes.
        """}
    ]
    
    # Add conversation history
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Get response from OpenAI
    with st.spinner("Assistant is thinking..."):
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
                model="gpt-4o",  # or any model defined in llm_config
                messages=messages,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Generate speech for the response
            speech_file = f"assistant_audio_{len(st.session_state.messages)}.mp3"
            speech_generated = generate_speech(assistant_message, speech_file)
            
            # Add assistant message to conversation
            new_message = {
                "role": "assistant",
                "content": assistant_message
            }
            
            if speech_generated:
                new_message["audio_path"] = speech_file
                
            st.session_state.messages.append(new_message)
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")

def transcribe_audio(audio_file):
    """Transcribe audio file using OpenAI's Whisper API"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(audio_file, "rb") as f:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
            
        return response.text
        
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def generate_speech(text, filename):
    """Generate speech from text using OpenAI's TTS API"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        
        response.stream_to_file(filename)
        return True
        
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return False

def end_conversation(kb, llm_config):
    """Extract knowledge from the conversation"""
    if not st.session_state.messages:
        st.warning("No conversation to extract knowledge from.")
        return
        
    # Get conversation text
    conversation_text = "\n".join([msg["content"] for msg in st.session_state.messages])
    
    # Extract knowledge
    with st.spinner("Extracting knowledge..."):
        extraction_result = extract_knowledge(conversation_text, llm_config)
    
    # Update knowledge base
    update_knowledge_base(extraction_result, kb)
    
    # Display results
    st.success("Knowledge extracted successfully!")
    
    # Display concepts
    st.subheader("Extracted Concepts")
    for concept, attributes in extraction_result.get("concepts", {}).items():
        with st.expander(f"Concept: {concept}"):
            st.json(attributes)
    
    # Display relationships
    st.subheader("Extracted Relationships")
    for rel in extraction_result.get("relationships", []):
        if all(k in rel for k in ["source", "relation", "target"]):
            st.write(f"- {rel['source']} {rel['relation']} {rel['target']}")