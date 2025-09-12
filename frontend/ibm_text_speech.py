"""
IBM Cloud Text-to-Speech Components for Streamlit Application

This module provides text-to-speech functionality using IBM Cloud Text-to-Speech API
for converting assistant responses to audio.

Ref: https://cloud.ibm.com/apidocs/text-to-speech#synthesize

curl -X POST -u "apikey:{apikey}" --header 
"Content-Type: application/json" --header 
"Accept: audio/wav" --data "{\"text\":\"Hello world\"}" 
--output hello_world.wav "{url}/v1/synthesize?voice=en-US_AllisonV3Voice"

"""


import os
import tempfile
import streamlit as st
import requests
import json
import base64
from typing import Optional, Dict, Any
import logging
from omegaconf import OmegaConf
import time
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Load configuration
config = OmegaConf.load("config.yaml")
IBM_TEXT_TO_SPEECH_URL = config.ibm_text_to_speech_url
IBM_TEXT_TO_SPEECH_KEY = os.environ.get("IBM_TEXT_TO_SPEECH_KEY")

# Available IBM Watson TTS voices
IBM_VOICES = {
    "en-US_MichaelV3Voice": "Michael (US Male - Professional)", # Default IBM Voice
    "en-US_AllisonV3Voice": "Allison (US Female - Natural)",
    "en-US_LisaV3Voice": "Lisa (US Female - Professional)", 
    "en-GB_KateV3Voice": "Kate (British Female)",
    "en-US_KevinV3Voice": "Kevin (US Male - Conversational)",
    "en-US_OliviaV3Voice": "Olivia (US Female - Conversational)"
}

class IBMTextToSpeechSynthesizer:
    """Text-to-speech synthesis using IBM Cloud Text-to-Speech API."""
    
    def __init__(self):
        """Initialize the IBM text-to-speech synthesizer with API credentials."""
        self.api_key = None
        self.api_url = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize IBM Cloud client using environment variable and config."""
        try:
            self.api_key = IBM_TEXT_TO_SPEECH_KEY
            self.api_url = IBM_TEXT_TO_SPEECH_URL
            
            if not self.api_key:
                logger.warning("IBM_TEXT_TO_SPEECH_KEY environment variable not found")
                return
            
            if not self.api_url:
                logger.warning("IBM Text-to-Speech URL not found in config")
                return
            
            # Ensure URL has the correct endpoint
            if not self.api_url.endswith('/v1/synthesize'):
                self.api_url = f"{self.api_url.rstrip('/')}/v1/synthesize"
            
            logger.info("IBM Cloud Text-to-Speech client initialized successfully")
            
        except Exception as e:
            logger.error(f"IBM TTS client initialization failed: {e}")
    
    def synthesize_text(self, text: str, voice: str = "en-US_MichaelV3Voice") -> Optional[bytes]:
        """
        Synthesize text to speech using IBM Cloud Text-to-Speech API.
        
        Args:
            text: Text to convert to speech
            voice: IBM Watson voice to use for synthesis
            
        Returns:
            Audio bytes in WAV format or None if synthesis failed
        """
        if not self.api_key or not self.api_url:
            logger.error("IBM Text-to-Speech client not initialized")
            return None
        
        if not text or not text.strip():
            logger.warning("Empty text provided for synthesis")
            return None
        
        # Limit text length for better performance (IBM TTS has limits)
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.info(f"Text truncated to {max_length} characters for TTS")
        
        try:
            # Prepare headers for IBM Cloud API
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"apikey:{self.api_key}".encode()).decode()}',
                'Content-Type': 'application/json',
                'Accept': 'audio/wav'
            }
            
            # Prepare URL parameters - voice must be a query parameter according to IBM docs
            params = {
                'voice': voice
            }
            
            # Prepare request body - only text goes in the body
            data = {
                'text': text
            }
            
            # Log the voice being used for debugging
            logger.info(f"IBM TTS request: voice={voice}, text_length={len(text)}")
            
            # Make the API request to IBM Cloud with voice as URL parameter
            response = requests.post(
                self.api_url,
                headers=headers,
                params=params,  # Voice goes in URL query parameters
                json=data,      # Only text goes in JSON body
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                # Return audio bytes
                audio_bytes = response.content
                logger.info(f"IBM TTS synthesis successful: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                error_message = f"IBM TTS API error: {response.status_code}"
                if response.text:
                    error_message += f" - {response.text}"
                logger.error(error_message)
                return None
            
        except requests.exceptions.Timeout:
            logger.error("IBM TTS API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("IBM TTS API connection error")
            return None
        except Exception as e:
            logger.error(f"IBM TTS synthesis failed: {e}")
            return None
    
    def save_audio_file(self, audio_bytes: bytes, prefix: str = "tts_audio") -> Optional[str]:
        """
        Save audio bytes to a temporary file.
        
        Args:
            audio_bytes: Audio data in bytes format
            prefix: Filename prefix for the temporary file
            
        Returns:
            Path to the saved audio file or None if failed
        """
        try:
            # Create temporary file with .wav extension
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=".wav", 
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


def create_tts_control_interface() -> Dict[str, Any]:
    """
    Create TTS control interface with activation toggle and voice selection.
    
    Returns:
        Dictionary containing TTS configuration
    """
    st.markdown("#### 🔊 Audio Responses")
    
    # Initialize TTS synthesizer in session state
    if 'ibm_tts_synthesizer' not in st.session_state:
        st.session_state.ibm_tts_synthesizer = IBMTextToSpeechSynthesizer()
    
    synthesizer = st.session_state.ibm_tts_synthesizer
    
    # Check if TTS is available
    tts_available = bool(synthesizer.api_key and synthesizer.api_url)
    
    if not tts_available:
        st.warning("⚠️ IBM Text-to-Speech unavailable - API credentials not configured")
        return {"enabled": False, "voice": None, "available": False}
    
    # TTS enable/disable toggle
    tts_enabled = st.checkbox(
        "Enable audio responses",
        value=st.session_state.get('tts_enabled', False),
        help="Convert assistant messages to speech using IBM Watson",
        key="tts_enabled_checkbox"
    )
    
    # Store TTS enabled state
    st.session_state.tts_enabled = tts_enabled
    
    # Get previously selected voice or use default
    default_voice = "en-US_MichaelV3Voice"
    previously_selected_voice = st.session_state.get('tts_selected_voice', default_voice)
    
    selected_voice = default_voice  # Fallback if TTS is disabled
    
    if tts_enabled:
        # Voice selection dropdown
        voice_options = list(IBM_VOICES.keys())
        voice_labels = [IBM_VOICES[voice] for voice in voice_options]
        
        # Find index of previously selected voice
        try:
            default_index = voice_options.index(previously_selected_voice)
        except ValueError:
            default_index = 0  # Fallback to first option if voice not found
        
        selected_index = st.selectbox(
            "Select voice:",
            range(len(voice_options)),
            format_func=lambda x: voice_labels[x],
            index=default_index,
            key="tts_voice_selection"
        )
        
        selected_voice = voice_options[selected_index]
        
        # Store selected voice in session state
        st.session_state.tts_selected_voice = selected_voice
        
        # TTS status expander
        with st.expander("🔧 TTS Configuration"):
            display_tts_status()
        
        # Test TTS functionality
        if st.button("🎧 Test Voice", help="Test the selected voice", key="test_tts_btn"):
            test_text = f"Hello! This is {IBM_VOICES[selected_voice]} speaking. Your audio responses are now enabled."
            with st.spinner("🎵 Generating test audio..."):
                audio_bytes = synthesizer.synthesize_text(test_text, selected_voice)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    st.success("✅ Test audio generated successfully!")
                else:
                    st.error("❌ Failed to generate test audio")
    
    return {
        "enabled": tts_enabled,
        "voice": st.session_state.get('tts_selected_voice', selected_voice) if tts_enabled else None,
        "available": tts_available
    }


def display_tts_status():
    """Display current IBM text-to-speech status and configuration."""
    st.markdown("**IBM Text-to-Speech Status**")
    
    # Check IBM API key
    api_key = IBM_TEXT_TO_SPEECH_KEY
    if api_key:
        st.success("✅ IBM Text-to-Speech API key configured")
        
        # Check URL configuration  
        if IBM_TEXT_TO_SPEECH_URL:
            st.success(f"✅ IBM Service URL configured")
            st.code(IBM_TEXT_TO_SPEECH_URL, language="text")
        else:
            st.error("❌ IBM Service URL not found in config.yaml")
    else:
        st.error("❌ IBM Text-to-Speech API key not found in environment variables")
        st.markdown("""
        **To enable IBM Text-to-Speech:**
        1. Set your IBM Text-to-Speech API key as: `IBM_TEXT_TO_SPEECH_KEY`
        2. Verify the service URL in config.yaml
        3. Restart the Streamlit application
        """)
    
    # Display available voices
    st.markdown("**Available Voices:**")
    for voice_id, voice_name in IBM_VOICES.items():
        st.text(f"• {voice_name}")


def synthesize_response_audio(text: str, tts_config: Dict[str, Any]) -> Optional[bytes]:
    """
    Synthesize audio for assistant response if TTS is enabled.
    
    Args:
        text: Response text to convert to speech
        tts_config: TTS configuration from control interface
        
    Returns:
        Audio bytes or None if TTS disabled/failed
    """
    if not tts_config.get("enabled", False) or not tts_config.get("available", False):
        return None
    
    # Get synthesizer from session state
    if 'ibm_tts_synthesizer' not in st.session_state:
        st.session_state.ibm_tts_synthesizer = IBMTextToSpeechSynthesizer()
    
    synthesizer = st.session_state.ibm_tts_synthesizer
    voice = tts_config.get("voice", "en-US_AllisonV3Voice")
    
    # Log which voice is being used for debugging
    logger.info(f"Synthesizing audio with voice: {voice}")
    
    # Clean text for TTS (remove markdown formatting)
    clean_text = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
    
    return synthesizer.synthesize_text(clean_text, voice)


def create_compact_tts_interface() -> bool:
    """
    Create a compact TTS toggle for smaller spaces.
    
    Returns:
        True if TTS is enabled and available, False otherwise
    """
    # Initialize TTS synthesizer
    if 'ibm_tts_synthesizer' not in st.session_state:
        st.session_state.ibm_tts_synthesizer = IBMTextToSpeechSynthesizer()
    
    synthesizer = st.session_state.ibm_tts_synthesizer
    tts_available = bool(synthesizer.api_key and synthesizer.api_url)
    
    if not tts_available:
        return False
    
    # Simple toggle
    tts_enabled = st.checkbox(
        "🔊 Audio responses",
        value=st.session_state.get('tts_enabled', False),
        key="compact_tts_toggle"
    )
    
    st.session_state.tts_enabled = tts_enabled
    return tts_enabled


def display_tts_comparison():
    """Display comparison of different TTS approaches."""
    st.markdown("#### 🔊 Text-to-Speech Options")
    
    comparison_data = {
        "Feature": [
            "Provider",
            "Voice Quality", 
            "Languages",
            "Speed",
            "Customization",
            "Cost",
            "Integration",
            "Use Case"
        ],
        "IBM Watson TTS": [
            "IBM Cloud",
            "Neural, very natural",
            "Multiple languages", 
            "Fast",
            "Extensive voice options",
            "Pay per character",
            "Enterprise APIs",
            "Professional applications"
        ],
        "Browser TTS": [
            "Device native",
            "Basic, robotic",
            "System dependent",
            "Very fast", 
            "Limited",
            "Free",
            "Simple JavaScript",
            "Quick prototypes"
        ]
    }
    
    st.table(comparison_data)
