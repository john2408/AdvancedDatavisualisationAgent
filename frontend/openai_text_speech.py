"""
OpenAI Text-to-Speech Components for Streamlit Application

This module provides text-to-speech functionality using OpenAI's Text-to-Speech API
for converting assistant responses to audio using the gpt-4o-mini-tts model.

Ref: https://platform.openai.com/docs/guides/text-to-speech
"""

import os
import tempfile
import streamlit as st
import logging
from openai import OpenAI
from typing import Optional, Dict, Any
import time
from pathlib import Path

# Setup logging
logger = logging.getLogger(__name__)

# Environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Available OpenAI TTS voices
OPENAI_VOICES = {
    "alloy": "Alloy (Neutral - Balanced)",
    "echo": "Echo (Male - Clear)",
    "fable": "Fable (British Male - Expressive)",
    "onyx": "Onyx (Male - Deep)",
    "nova": "Nova (Female - Young)",
    "shimmer": "Shimmer (Female - Soft)",
    "coral": "Coral (Female - Warm)"
}

class OpenAITextToSpeechSynthesizer:
    """Text-to-speech synthesis using OpenAI's TTS API."""
    
    def __init__(self):
        """Initialize the OpenAI text-to-speech synthesizer with API credentials."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client using environment variable."""
        try:
            if not OPENAI_API_KEY:
                logger.warning("OPENAI_API_KEY environment variable not found")
                return
            
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            logger.info("OpenAI Text-to-Speech client initialized successfully")
            
        except Exception as e:
            logger.error(f"OpenAI TTS client initialization failed: {e}")
    
    def synthesize_text(self, text: str, voice: str = "alloy", instructions: str = None) -> Optional[bytes]:
        """
        Synthesize text to speech using OpenAI's TTS API.
        
        Args:
            text: Text to convert to speech
            voice: OpenAI voice to use for synthesis
            instructions: Optional instructions for speech synthesis
            
        Returns:
            Audio bytes in MP3 format or None if synthesis failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return None
        
        if not text or not text.strip():
            logger.warning("Empty text provided for synthesis")
            return None
        
        # Limit text length for better performance
        max_length = 4096  # OpenAI TTS character limit
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.info(f"Text truncated to {max_length} characters for TTS")
        
        try:
            # Log the voice being used for debugging
            logger.info(f"OpenAI TTS request: voice={voice}, text_length={len(text)}")
            
            # Prepare the request parameters
            request_params = {
                "model": "tts-1",  # Using tts-1 model as it's more stable than gpt-4o-mini-tts
                "voice": voice,
                "input": text,
                "response_format": "mp3"
            }
            
            # Add instructions if provided
            if instructions:
                request_params["instructions"] = instructions
            
            # Use the OpenAI API with streaming response
            with self.client.audio.speech.with_streaming_response.create(**request_params) as response:
                # Read all audio bytes from the stream
                audio_bytes = b""
                for chunk in response.iter_bytes():
                    audio_bytes += chunk
            
            if audio_bytes:
                logger.info(f"OpenAI TTS synthesis successful: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                logger.error("OpenAI TTS returned empty audio")
                return None
            
        except Exception as e:
            logger.error(f"OpenAI TTS synthesis failed: {e}")
            return None
    
    def save_audio_file(self, audio_bytes: bytes, prefix: str = "openai_audio") -> Optional[str]:
        """
        Save audio bytes to a temporary file.
        
        Args:
            audio_bytes: Audio data in bytes format
            prefix: Filename prefix for the temporary file
            
        Returns:
            Path to the saved audio file or None if failed
        """
        try:
            # Create temporary file with .mp3 extension
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=".mp3", 
                prefix=f"{prefix}_{int(time.time())}_"
            )
            
            # Write audio bytes to file
            temp_file.write(audio_bytes)
            temp_file.close()
            
            logger.info(f"Audio saved to temporary file: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            return None


def create_openai_tts_interface() -> Dict[str, Any]:
    """
    Create OpenAI TTS control interface with voice selection.
    
    Returns:
        Dictionary containing TTS configuration
    """
    # Initialize OpenAI synthesizer in session state
    if 'openai_tts_synthesizer' not in st.session_state:
        st.session_state.openai_tts_synthesizer = OpenAITextToSpeechSynthesizer()
    
    synthesizer = st.session_state.openai_tts_synthesizer
    
    # Check if TTS is available
    tts_available = bool(synthesizer.client)
    
    if not tts_available:
        st.warning("⚠️ OpenAI Text-to-Speech unavailable - API key not configured")
        return {"enabled": False, "voice": None, "available": False, "provider": "openai"}
    
    # Get previously selected voice or use default
    default_voice = "alloy"
    previously_selected_voice = st.session_state.get('openai_selected_voice', default_voice)
    
    # Voice selection dropdown
    voice_options = list(OPENAI_VOICES.keys())
    voice_labels = [OPENAI_VOICES[voice] for voice in voice_options]
    
    # Find index of previously selected voice
    try:
        default_index = voice_options.index(previously_selected_voice)
    except ValueError:
        default_index = 0  # Fallback to first option if voice not found
    
    selected_index = st.selectbox(
        "Select OpenAI voice:",
        range(len(voice_options)),
        format_func=lambda x: voice_labels[x],
        index=default_index,
        key="openai_voice_selection"
    )
    
    selected_voice = voice_options[selected_index]
    
    # Store selected voice in session state
    st.session_state.openai_selected_voice = selected_voice
    
    # Optional instructions for speech synthesis
    instructions = st.text_input(
        "Speech instructions (optional):",
        value=st.session_state.get('openai_tts_instructions', ''),
        help="Optional instructions for tone, style, or emotion",
        key="openai_tts_instructions_input",
        placeholder="e.g., Speak in a cheerful and positive tone"
    )
    
    # Store instructions in session state
    st.session_state.openai_tts_instructions = instructions
    
    # OpenAI status expander
    with st.expander("🔧 OpenAI Configuration"):
        display_openai_status()
    
    # Test TTS functionality
    if st.button("🎧 Test OpenAI Voice", help="Test the selected OpenAI voice", key="test_openai_btn"):
        test_text = f"Hello! This is {OPENAI_VOICES[selected_voice]} speaking from OpenAI. Your audio responses are now enabled."
        with st.spinner("🎵 Generating test audio..."):
            audio_bytes = synthesizer.synthesize_text(test_text, selected_voice, instructions if instructions else None)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                st.success("✅ Test audio generated successfully!")
            else:
                st.error("❌ Failed to generate test audio")
    
    return {
        "enabled": True,
        "voice": selected_voice,
        "instructions": instructions if instructions else None,
        "available": tts_available,
        "provider": "openai"
    }


def display_openai_status():
    """Display current OpenAI text-to-speech status and configuration."""
    st.markdown("**OpenAI Text-to-Speech Status**")
    
    # Check OpenAI API key
    api_key = OPENAI_API_KEY
    if api_key:
        st.success("✅ OpenAI API key configured")
        st.code(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else 'masked'}")
    else:
        st.error("❌ OpenAI API key not found in environment variables")
        st.markdown("""
        **To enable OpenAI Text-to-Speech:**
        1. Set your OpenAI API key as: `OPENAI_API_KEY`
        2. Restart the Streamlit application
        """)
    
    # Display available voices
    st.markdown("**Available Voices:**")
    for voice_id, voice_name in OPENAI_VOICES.items():
        st.text(f"• {voice_name}")
    
    # Display model information
    st.markdown("**Model Information:**")
    st.text("• Model: tts-1 (High-quality neural text-to-speech)")
    st.text("• Format: MP3")
    st.text("• Max characters: 4,096 per request")


def synthesize_openai_audio(text: str, tts_config: Dict[str, Any]) -> Optional[bytes]:
    """
    Synthesize audio for assistant response using OpenAI if enabled.
    
    Args:
        text: Response text to convert to speech
        tts_config: TTS configuration
        
    Returns:
        Audio bytes or None if TTS disabled/failed
    """
    if not tts_config.get("enabled", False) or not tts_config.get("available", False):
        return None
    
    if tts_config.get("provider") != "openai":
        return None
    
    # Get synthesizer from session state
    if 'openai_tts_synthesizer' not in st.session_state:
        st.session_state.openai_tts_synthesizer = OpenAITextToSpeechSynthesizer()
    
    synthesizer = st.session_state.openai_tts_synthesizer
    voice = tts_config.get("voice", "alloy")
    instructions = tts_config.get("instructions")
    
    # Log which voice is being used for debugging
    logger.info(f"Synthesizing audio with OpenAI voice: {voice}")
    
    # Clean text for TTS (remove markdown formatting)
    clean_text = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
    
    return synthesizer.synthesize_text(clean_text, voice, instructions)
