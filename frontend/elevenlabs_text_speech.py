import os
import tempfile
import streamlit as st
import logging
from elevenlabs.client import ElevenLabs
from typing import Optional, Dict, Any
import time
from omegaconf import OmegaConf

# Setup logging
logger = logging.getLogger(__name__)

# Environment variables
config = OmegaConf.load("config.yaml")
ELEVEN_LABS_TEXT_TO_SPEECH_KEY = os.environ.get(config.get("elevenlabs_text_to_speech_key"))

# Available ElevenLabs voices (popular ones)
ELEVENLABS_VOICES = {
    "JBFqnCBsd6RMkjVDRZzb": "George (British Male - Elegant)",
    "21m00Tcm4TlvDq8ikWAM": "Rachel (American Female - Professional)",
    "AZnzlk1XvdvUeBnXmlld": "Domi (American Female - Strong)",
    "EXAVITQu4vr4xnSDxMaL": "Bella (American Female - Soft)",
    "ErXwobaYiN019PkySvjV": "Antoni (American Male - Well-Rounded)",
    "MF3mGyEYCl7XYWbV9V6O": "Elli (American Female - Emotional)",
    "TxGEqnHWrfWFTfGW9XjX": "Josh (American Male - Deep)",
    "VR6AewLTigWG4xSOukaG": "Arnold (American Male - Crisp)",
    "pNInz6obpgDQGcFmaJgB": "Adam (American Male - Narrative)",
    "yoZ06aMxZJJ28mfd3POQ": "Sam (American Male - Young)"
}

class ElevenLabsTextToSpeechSynthesizer:
    """Text-to-speech synthesis using ElevenLabs API."""
    
    def __init__(self):
        """Initialize the ElevenLabs text-to-speech synthesizer with API credentials."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize ElevenLabs client using environment variable."""
        try:
            if not ELEVEN_LABS_TEXT_TO_SPEECH_KEY:
                logger.warning("elevenlabs_text_to_speech_key environment variable not found")
                return
            
            self.client = ElevenLabs(api_key=ELEVEN_LABS_TEXT_TO_SPEECH_KEY)
            logger.info("ElevenLabs Text-to-Speech client initialized successfully")
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS client initialization failed: {e}")
    
    def synthesize_text(self, text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb") -> Optional[bytes]:
        """
        Synthesize text to speech using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID to use for synthesis
            
        Returns:
            Audio bytes in MP3 format or None if synthesis failed
        """
        if not self.client:
            logger.error("ElevenLabs client not initialized")
            return None
        
        if not text or not text.strip():
            logger.warning("Empty text provided for synthesis")
            return None
        
        # Limit text length for better performance
        max_length = 2500  # ElevenLabs has higher limits than IBM
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.info(f"Text truncated to {max_length} characters for TTS")
        
        try:
            # Log the voice being used for debugging
            logger.info(f"ElevenLabs TTS request: voice_id={voice_id}, text_length={len(text)}")
            
            # Use the ElevenLabs API to convert text to speech
            audio_generator = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128",
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio_generator)
            
            if audio_bytes:
                logger.info(f"ElevenLabs TTS synthesis successful: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                logger.error("ElevenLabs TTS returned empty audio")
                return None
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS synthesis failed: {e}")
            return None
    
    def save_audio_file(self, audio_bytes: bytes, prefix: str = "elevenlabs_audio") -> Optional[str]:
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


def create_elevenlabs_tts_interface() -> Dict[str, Any]:
    """
    Create ElevenLabs TTS control interface with voice selection.
    
    Returns:
        Dictionary containing TTS configuration
    """
    # Initialize ElevenLabs synthesizer in session state
    if 'elevenlabs_tts_synthesizer' not in st.session_state:
        st.session_state.elevenlabs_tts_synthesizer = ElevenLabsTextToSpeechSynthesizer()
    
    synthesizer = st.session_state.elevenlabs_tts_synthesizer
    
    # Check if TTS is available
    tts_available = bool(synthesizer.client)
    
    if not tts_available:
        st.warning("⚠️ ElevenLabs Text-to-Speech unavailable - API key not configured")
        return {"enabled": False, "voice": None, "available": False, "provider": "elevenlabs"}
    
    # Get previously selected voice or use default
    default_voice = "JBFqnCBsd6RMkjVDRZzb"
    previously_selected_voice = st.session_state.get('elevenlabs_selected_voice', default_voice)
    
    # Voice selection dropdown
    voice_options = list(ELEVENLABS_VOICES.keys())
    voice_labels = [ELEVENLABS_VOICES[voice] for voice in voice_options]
    
    # Find index of previously selected voice
    try:
        default_index = voice_options.index(previously_selected_voice)
    except ValueError:
        default_index = 0  # Fallback to first option if voice not found
    
    selected_index = st.selectbox(
        "Select ElevenLabs voice:",
        range(len(voice_options)),
        format_func=lambda x: voice_labels[x],
        index=default_index,
        key="elevenlabs_voice_selection"
    )
    
    selected_voice = voice_options[selected_index]
    
    # Store selected voice in session state
    st.session_state.elevenlabs_selected_voice = selected_voice
    
    # ElevenLabs status expander
    with st.expander("🔧 ElevenLabs Configuration"):
        display_elevenlabs_status()
    
    # Test TTS functionality
    if st.button("🎧 Test ElevenLabs Voice", help="Test the selected ElevenLabs voice", key="test_elevenlabs_btn"):
        test_text = f"Hello! This is {ELEVENLABS_VOICES[selected_voice]} speaking from ElevenLabs. Your audio responses are now enabled."
        with st.spinner("🎵 Generating test audio..."):
            audio_bytes = synthesizer.synthesize_text(test_text, selected_voice)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3")
                st.success("✅ Test audio generated successfully!")
            else:
                st.error("❌ Failed to generate test audio")
    
    return {
        "enabled": True,
        "voice": selected_voice,
        "available": tts_available,
        "provider": "elevenlabs"
    }


def display_elevenlabs_status():
    """Display current ElevenLabs text-to-speech status and configuration."""
    st.markdown("**ElevenLabs Text-to-Speech Status**")
    
    # Check ElevenLabs API key
    api_key = ELEVEN_LABS_TEXT_TO_SPEECH_KEY
    if api_key:
        st.success("✅ ElevenLabs API key configured")
        st.code(f"API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else 'masked'}")
    else:
        st.error("❌ ElevenLabs API key not found in environment variables")
        st.markdown("""
        **To enable ElevenLabs Text-to-Speech:**
        1. Set your ElevenLabs API key as: `elevenlabs_text_to_speech_key`
        2. Restart the Streamlit application
        """)
    
    # Display available voices
    st.markdown("**Available Voices:**")
    for voice_id, voice_name in ELEVENLABS_VOICES.items():
        st.text(f"• {voice_name}")


def synthesize_elevenlabs_audio(text: str, tts_config: Dict[str, Any]) -> Optional[bytes]:
    """
    Synthesize audio for assistant response using ElevenLabs if enabled.
    
    Args:
        text: Response text to convert to speech
        tts_config: TTS configuration
        
    Returns:
        Audio bytes or None if TTS disabled/failed
    """
    if not tts_config.get("enabled", False) or not tts_config.get("available", False):
        return None
    
    if tts_config.get("provider") != "elevenlabs":
        return None
    
    # Get synthesizer from session state
    if 'elevenlabs_tts_synthesizer' not in st.session_state:
        st.session_state.elevenlabs_tts_synthesizer = ElevenLabsTextToSpeechSynthesizer()
    
    synthesizer = st.session_state.elevenlabs_tts_synthesizer
    voice_id = tts_config.get("voice", "JBFqnCBsd6RMkjVDRZzb")
    
    # Log which voice is being used for debugging
    logger.info(f"Synthesizing audio with ElevenLabs voice: {voice_id}")
    
    # Clean text for TTS (remove markdown formatting)
    clean_text = text.replace("**", "").replace("*", "").replace("#", "").replace("`", "")
    
    return synthesizer.synthesize_text(clean_text, voice_id)