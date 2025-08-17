"""
Voice Components for Streamlit Application

This module provides voice-to-text functionality using OpenAI Whisper API
and streamlit-audio-recorder for capturing audio input.
"""

import os
import tempfile
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
from typing import Optional
import logging

# Setup logging
logger = logging.getLogger(__name__)

class VoiceTranscriber:
    """Voice-to-text transcription using OpenAI Whisper API."""
    
    def __init__(self):
        """Initialize the voice transcriber with OpenAI client."""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client using environment variable."""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                st.error("❌ OPENAI_API_KEY environment variable not found!")
                return
            
            self.client = openai.OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            st.error(f"❌ Failed to initialize OpenAI client: {e}")
            logger.error(f"OpenAI client initialization failed: {e}")
    
    def transcribe_audio(self, audio_bytes: bytes) -> Optional[str]:
        """
        Transcribe audio bytes using OpenAI Whisper API.
        
        Args:
            audio_bytes: Raw audio data in bytes format
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if not self.client:
            st.error("❌ OpenAI client not initialized")
            return None
        
        try:
            # Create temporary file for audio data
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_file_path = tmp_file.name
            
            # Transcribe audio using Whisper
            with open(tmp_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="en"  # You can make this configurable if needed
                )
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            if isinstance(transcript, str):
                return transcript.strip()
            else:
                # Handle case where transcript is an object with text attribute
                return transcript.text.strip() if hasattr(transcript, 'text') else str(transcript).strip()
            
        except Exception as e:
            st.error(f"❌ Error transcribing audio: {e}")
            logger.error(f"Audio transcription failed: {e}")
            return None


def create_voice_input_interface() -> Optional[str]:
    """
    Create voice input interface with recording and transcription capabilities.
    
    Returns:
        Transcribed text if successful, None otherwise
    """
    # Initialize transcriber in session state
    if 'voice_transcriber' not in st.session_state:
        st.session_state.voice_transcriber = VoiceTranscriber()
    
    # Initialize audio recording state
    if 'audio_cleared' not in st.session_state:
        st.session_state.audio_cleared = False
        
    # Initialize recording counter to force component refresh
    if 'recording_counter' not in st.session_state:
        st.session_state.recording_counter = 0
    
    transcriber = st.session_state.voice_transcriber
    
    if not transcriber.client:
        st.warning("⚠️ Voice input unavailable - OpenAI API key not configured")
        return None
    
    st.markdown("#### 🎤 Voice Input")
    
    # Audio recorder component with dynamic key to force refresh
    audio_bytes = audio_recorder(
        text="Click to record your question",
        recording_color="#e74c3c",
        neutral_color="#ffffff",  # White background
        icon_name="microphone",
        icon_size="2x",
        pause_threshold=2.0,  # Stop recording after 2 seconds of silence
        sample_rate=16000,    # Optimal for Whisper
        key=f"voice_recorder_{st.session_state.recording_counter}"  # Dynamic key
    )
    
    # Handle audio recording
    if audio_bytes and not st.session_state.audio_cleared:
        st.audio(audio_bytes, format="audio/wav")
        
        # Create columns for buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Transcribe", use_container_width=True, key="transcribe_btn"):
                with st.spinner("🎧 Transcribing audio..."):
                    transcript = transcriber.transcribe_audio(audio_bytes)
                    
                    if transcript:
                        st.session_state.voice_transcript = transcript
                        st.success("✅ Audio transcribed successfully!")
                    else:
                        st.error("❌ Failed to transcribe audio")
        
        with col2:
            if st.button("🗑️ Clear", use_container_width=True, key="clear_audio_btn"):
                # Clear all audio-related session state
                if 'voice_transcript' in st.session_state:
                    del st.session_state.voice_transcript
                
                # Set flag to indicate audio was cleared
                st.session_state.audio_cleared = True
                
                # Increment counter to create new recorder component
                st.session_state.recording_counter += 1
                
                # Force rerun to refresh the component
                st.rerun()
    
    # Reset the cleared flag if no audio is present
    if not audio_bytes:
        st.session_state.audio_cleared = False
    
    # Display transcript if available
    if 'voice_transcript' in st.session_state and st.session_state.voice_transcript:
        transcript = st.session_state.voice_transcript
        
        st.markdown("**📝 Transcript:**")
        edited_transcript = st.text_area(
            "Edit if needed:",
            transcript,
            height=80,
            key="transcript_editor",
            help="You can edit the transcript before sending"
        )
        
        # Action buttons for transcript
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📤 Send Query", use_container_width=True, key="send_voice_query"):
                if edited_transcript.strip():
                    # Clear the transcript from session state
                    del st.session_state.voice_transcript
                    # Reset audio state
                    st.session_state.audio_cleared = True
                    st.session_state.recording_counter += 1
                    return edited_transcript.strip()
        
        with col2:
            if st.button("🔄 Re-record", use_container_width=True, key="rerecord_btn"):
                # Clear transcript and reset audio
                if 'voice_transcript' in st.session_state:
                    del st.session_state.voice_transcript
                st.session_state.audio_cleared = True
                st.session_state.recording_counter += 1
                st.rerun()
        
        with col3:
            if st.button("❌ Cancel", use_container_width=True, key="cancel_voice_btn"):
                # Clear transcript and reset audio
                if 'voice_transcript' in st.session_state:
                    del st.session_state.voice_transcript
                st.session_state.audio_cleared = True
                st.session_state.recording_counter += 1
                st.rerun()
    
    return None


def create_compact_voice_interface() -> Optional[str]:
    """
    Create a more compact voice interface for smaller spaces.
    
    Returns:
        Transcribed text if successful, None otherwise
    """
    # Initialize transcriber
    if 'voice_transcriber' not in st.session_state:
        st.session_state.voice_transcriber = VoiceTranscriber()
    
    # Initialize compact recording counter
    if 'compact_recording_counter' not in st.session_state:
        st.session_state.compact_recording_counter = 0
    
    transcriber = st.session_state.voice_transcriber
    
    if not transcriber.client:
        return None
    
    # Compact audio recorder with dynamic key
    audio_bytes = audio_recorder(
        text="🎤",
        recording_color="#e74c3c",
        neutral_color="#ffffff",  # White background
        icon_name="microphone",
        icon_size="1x",
        pause_threshold=2.0,
        sample_rate=16000,
        key=f"compact_voice_recorder_{st.session_state.compact_recording_counter}"
    )
    
    if audio_bytes:
        with st.spinner("🎧 Processing..."):
            transcript = transcriber.transcribe_audio(audio_bytes)
            if transcript:
                # Reset the counter for next recording
                st.session_state.compact_recording_counter += 1
                return transcript.strip()
    
    return None


def display_voice_status():
    """Display current voice input status and configuration."""
    st.markdown("#### 🎤 Voice Input Status")
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API key configured")
    else:
        st.error("❌ OpenAI API key not found in environment variables")
        st.markdown("""
        **To enable voice input:**
        1. Set your OpenAI API key as an environment variable: `OPENAI_API_KEY`
        2. Restart the Streamlit application
        """)
    
    # Browser compatibility info
    st.info("""
    **Voice Input Requirements:**
    - Modern web browser (Chrome, Firefox, Safari, Edge)
    - Microphone access permission
    - Stable internet connection for transcription
    """)
