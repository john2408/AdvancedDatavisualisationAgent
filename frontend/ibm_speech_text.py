"""
IBM Cloud Speech-to-Text Components for Streamlit Application

This module provides voice-to-text functionality using IBM Cloud Speech-to-Text API
and streamlit-audio-recorder for capturing audio input.
"""

import os
import tempfile
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import json
import base64
from typing import Optional
import logging
from omegaconf import OmegaConf

# Setup logging
logger = logging.getLogger(__name__)

# Load configuration
config = OmegaConf.load("config.yaml")
IBM_SPEECH_TO_TEXT_URL = config.ibm_speech_to_text_url
IBM_SPEECH_TO_TEXT_KEY = os.environ.get("IBM_SPEECH_TO_TEXT_KEY")

class IBMVoiceTranscriber:
    """Voice-to-text transcription using IBM Cloud Speech-to-Text API."""
    
    def __init__(self):
        """Initialize the IBM voice transcriber with API credentials."""
        self.api_key = None
        self.api_url = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize IBM Cloud client using environment variable and config."""
        try:
            self.api_key = IBM_SPEECH_TO_TEXT_KEY
            self.api_url = IBM_SPEECH_TO_TEXT_URL
            
            if not self.api_key:
                st.error("❌ IBM_SPEECH_TO_TEXT_KEY environment variable not found!")
                return
            
            if not self.api_url:
                st.error("❌ IBM Speech-to-Text URL not found in config!")
                return
            
            # Ensure URL has the correct endpoint
            if not self.api_url.endswith('/v1/recognize'):
                self.api_url = f"{self.api_url.rstrip('/')}/v1/recognize"
            
            logger.info("IBM Cloud Speech-to-Text client initialized successfully")
            
        except Exception as e:
            st.error(f"❌ Failed to initialize IBM Speech-to-Text client: {e}")
            logger.error(f"IBM client initialization failed: {e}")
    
    def transcribe_audio(self, audio_bytes: bytes) -> Optional[str]:
        """
        Transcribe audio bytes using IBM Cloud Speech-to-Text API.
        
        Args:
            audio_bytes: Raw audio data in bytes format
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if not self.api_key or not self.api_url:
            st.error("❌ IBM Speech-to-Text client not initialized")
            return None
        
        try:
            # Prepare headers for IBM Cloud API
            headers = {
                'Authorization': f'Basic {base64.b64encode(f"apikey:{self.api_key}".encode()).decode()}',
                'Content-Type': 'audio/wav',
                'Accept': 'application/json'
            }
            
            # Prepare parameters for the request
            params = {
                'model': 'en-US_BroadbandModel',  # English broadband model
                'content_type': 'audio/wav',
                'continuous': True,
                'interim_results': False,
                'max_alternatives': 1,
                'word_confidence': False,
                'timestamps': False
            }
            
            # Make the API request to IBM Cloud
            response = requests.post(
                self.api_url,
                headers=headers,
                params=params,
                data=audio_bytes,
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Extract transcript from IBM response
                if 'results' in result and len(result['results']) > 0:
                    alternatives = result['results'][0].get('alternatives', [])
                    if alternatives:
                        transcript = alternatives[0].get('transcript', '').strip()
                        
                        # Calculate confidence if available
                        confidence = alternatives[0].get('confidence', 0.0)
                        if confidence > 0:
                            logger.info(f"IBM transcription confidence: {confidence:.2f}")
                        
                        return transcript
                else:
                    st.warning("⚠️ No speech detected in audio")
                    return None
            else:
                error_message = f"IBM API error: {response.status_code} - {response.text}"
                st.error(f"❌ {error_message}")
                logger.error(error_message)
                return None
            
        except requests.exceptions.Timeout:
            st.error("❌ Request timed out. Please try again.")
            logger.error("IBM API request timed out")
            return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Connection error. Please check your internet connection.")
            logger.error("IBM API connection error")
            return None
        except Exception as e:
            st.error(f"❌ Error transcribing audio: {e}")
            logger.error(f"IBM audio transcription failed: {e}")
            return None


def create_ibm_voice_input_interface() -> Optional[str]:
    """
    Create IBM Cloud voice input interface with recording and transcription capabilities.
    
    Returns:
        Transcribed text if successful, None otherwise
    """
    # Initialize transcriber in session state
    if 'ibm_voice_transcriber' not in st.session_state:
        st.session_state.ibm_voice_transcriber = IBMVoiceTranscriber()
    
    # Initialize audio recording state
    if 'ibm_audio_cleared' not in st.session_state:
        st.session_state.ibm_audio_cleared = False
        
    # Initialize recording counter to force component refresh
    if 'ibm_recording_counter' not in st.session_state:
        st.session_state.ibm_recording_counter = 0
    
    transcriber = st.session_state.ibm_voice_transcriber
    
    if not transcriber.api_key or not transcriber.api_url:
        st.warning("⚠️ IBM Voice input unavailable - API credentials not configured")
        return None
    
    st.markdown("#### 🎤 IBM Cloud Voice Input")
    
    # Audio recorder component with dynamic key to force refresh
    audio_bytes = audio_recorder(
        text="Click to record your question",
        recording_color="#1f77b4",  # IBM blue color
        neutral_color="#ffffff",   # White background
        icon_name="microphone",
        icon_size="2x",
        pause_threshold=2.0,  # Stop recording after 2 seconds of silence
        sample_rate=16000,    # Optimal for IBM Speech-to-Text
        key=f"ibm_voice_recorder_{st.session_state.ibm_recording_counter}"  # Dynamic key
    )
    
    # Handle audio recording
    if audio_bytes and not st.session_state.ibm_audio_cleared:
        st.audio(audio_bytes, format="audio/wav")
        
        # Create columns for buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Transcribe with IBM", use_container_width=True, key="ibm_transcribe_btn"):
                with st.spinner("🎧 Transcribing with IBM Watson..."):
                    transcript = transcriber.transcribe_audio(audio_bytes)
                    
                    if transcript:
                        st.session_state.ibm_voice_transcript = transcript
                        st.success("✅ Audio transcribed successfully with IBM!")
                    else:
                        st.error("❌ Failed to transcribe audio with IBM")
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True, key="ibm_clear_audio_btn"):
                # Clear all audio-related session state
                if 'ibm_voice_transcript' in st.session_state:
                    del st.session_state.ibm_voice_transcript
                
                # Set flag to indicate audio was cleared
                st.session_state.ibm_audio_cleared = True
                
                # Increment counter to create new recorder component
                st.session_state.ibm_recording_counter += 1
                
                # Force rerun to refresh the component
                st.rerun()
    
    # Reset the cleared flag if no audio is present
    if not audio_bytes:
        st.session_state.ibm_audio_cleared = False
    
    # Display transcript if available
    if 'ibm_voice_transcript' in st.session_state and st.session_state.ibm_voice_transcript:
        transcript = st.session_state.ibm_voice_transcript
        
        st.markdown("**📝 IBM Watson Transcript:**")
        edited_transcript = st.text_area(
            "Edit if needed:",
            transcript,
            height=80,
            key="ibm_transcript_editor",
            help="You can edit the IBM transcript before sending"
        )
        
        # Apply custom CSS for white background and white font
        st.markdown(
            """
            <style>
            div[data-testid="stTextArea"] > div > div > textarea {
            background-color: white !important;
            color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        # Action buttons for transcript
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Send Query", use_container_width=True, key="send_ibm_voice_query"):
                if edited_transcript.strip():
                    # Clear the transcript from session state
                    del st.session_state.ibm_voice_transcript
                    # Reset audio state
                    st.session_state.ibm_audio_cleared = True
                    st.session_state.ibm_recording_counter += 1
                    return edited_transcript.strip()
        
        with col2:
            if st.button("🔄 Re-record", use_container_width=True, key="ibm_rerecord_btn"):
                # Clear transcript and reset audio
                if 'ibm_voice_transcript' in st.session_state:
                    del st.session_state.ibm_voice_transcript
                st.session_state.ibm_audio_cleared = True
                st.session_state.ibm_recording_counter += 1
                st.rerun()
        
        with col3:
            if st.button("❌ Cancel", use_container_width=True, key="ibm_cancel_voice_btn"):
                # Clear transcript and reset audio
                if 'ibm_voice_transcript' in st.session_state:
                    del st.session_state.ibm_voice_transcript
                st.session_state.ibm_audio_cleared = True
                st.session_state.ibm_recording_counter += 1
                st.rerun()
    
    return None


def create_compact_ibm_voice_interface() -> Optional[str]:
    """
    Create a more compact IBM voice interface for smaller spaces.
    
    Returns:
        Transcribed text if successful, None otherwise
    """
    # Initialize transcriber
    if 'ibm_voice_transcriber' not in st.session_state:
        st.session_state.ibm_voice_transcriber = IBMVoiceTranscriber()
    
    # Initialize compact recording counter
    if 'ibm_compact_recording_counter' not in st.session_state:
        st.session_state.ibm_compact_recording_counter = 0
    
    transcriber = st.session_state.ibm_voice_transcriber
    
    if not transcriber.api_key or not transcriber.api_url:
        return None
    
    # Compact audio recorder with dynamic key
    audio_bytes = audio_recorder(
        text="🎤 IBM",
        recording_color="#1f77b4",  # IBM blue
        neutral_color="#ffffff",   # White background
        icon_name="microphone",
        icon_size="1x",
        pause_threshold=2.0,
        sample_rate=16000,
        key=f"ibm_compact_voice_recorder_{st.session_state.ibm_compact_recording_counter}"
    )
    
    if audio_bytes:
        with st.spinner("🎧 Processing with IBM..."):
            transcript = transcriber.transcribe_audio(audio_bytes)
            if transcript:
                # Reset the counter for next recording
                st.session_state.ibm_compact_recording_counter += 1
                return transcript.strip()
    
    return None


def display_ibm_voice_status():
    """Display current IBM voice input status and configuration."""
    st.markdown("#### 🎤 IBM Cloud Voice Input Status")
    
    # Check IBM API key
    api_key = IBM_SPEECH_TO_TEXT_KEY
    if api_key:
        st.success("✅ IBM Speech-to-Text API key configured")
        
        # Check URL configuration
        if IBM_SPEECH_TO_TEXT_URL:
            st.success(f"✅ IBM Service URL configured: {IBM_SPEECH_TO_TEXT_URL}")
        else:
            st.error("❌ IBM Service URL not found in config.yaml")
    else:
        st.error("❌ IBM Speech-to-Text API key not found in environment variables")
        st.markdown("""
        **To enable IBM voice input:**
        1. Set your IBM Speech-to-Text API key as an environment variable: `IBM_SPEECH_TO_TEXT_KEY`
        2. Verify the service URL in config.yaml
        3. Restart the Streamlit application
        """)
    


def compare_transcription_services():
    """Display comparison between OpenAI Whisper and IBM Speech-to-Text."""
    st.markdown("#### 📊 Transcription Service Comparison")
    
    comparison_data = {
        "Feature": [
            "Provider",
            "Model",
            "Language Support",
            "Audio Quality",
            "Speed",
            "Confidence Scores",
            "Cost (per minute)",
            "Privacy",
            "Accuracy"
        ],
        "OpenAI Whisper": [
            "OpenAI",
            "Whisper-1",
            "100+ languages",
            "Excellent with noise",
            "Fast",
            "Not provided",
            "~$0.006",
            "OpenAI privacy policy",
            "Very high"
        ],
        "IBM Watson": [
            "IBM Cloud",
            "BroadbandModel",
            "Multiple languages",
            "Excellent for clear speech",
            "Very fast",
            "Yes, provided",
            "Variable pricing",
            "Enterprise-grade",
            "Very high"
        ]
    }
    
    st.table(comparison_data)