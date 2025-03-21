import os
import openai
from typing import Optional

def transcribe_audio(audio_file_path: str) -> Optional[str]:
    """
    Transcribe audio file using OpenAI's Whisper API.
    
    Args:
        audio_file_path: Path to the audio file to transcribe
        
    Returns:
        Transcribed text or None if transcription failed
    """
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        return response.text
    except Exception as e:
        print(f"Error transcribing audio: {str(e)}")
        return None