"""
Example Usage of Both Voice Input Services

This example demonstrates how to use both OpenAI Whisper and IBM Cloud Speech-to-Text
services in your Streamlit application.
"""

import streamlit as st
from frontend.voice_components import (
    create_voice_input_interface, 
    create_compact_voice_interface,
    display_voice_status
)
from frontend.ibm_speech_text import (
    create_ibm_voice_input_interface,
    create_compact_ibm_voice_interface, 
    display_ibm_voice_status,
    compare_transcription_services
)

def main():
    """Example of using both voice input services."""
    
    st.title("🎤 Dual Voice Input Demo")
    st.markdown("Choose between OpenAI Whisper and IBM Cloud Speech-to-Text")
    
    # Service selection
    service_option = st.radio(
        "Select Voice Transcription Service:",
        ["OpenAI Whisper", "IBM Cloud Speech-to-Text", "Both Services", "Service Comparison"],
        horizontal=True
    )
    
    if service_option == "OpenAI Whisper":
        st.markdown("### 🤖 OpenAI Whisper Service")
        
        # Display status
        display_voice_status()
        
        # Voice input interface
        voice_query = create_voice_input_interface()
        
        if voice_query:
            st.success(f"✅ OpenAI Transcription: {voice_query}")
            
    elif service_option == "IBM Cloud Speech-to-Text":
        st.markdown("### 🔵 IBM Cloud Speech-to-Text Service")
        
        # Display status
        display_ibm_voice_status()
        
        # IBM voice input interface
        ibm_voice_query = create_ibm_voice_input_interface()
        
        if ibm_voice_query:
            st.success(f"✅ IBM Transcription: {ibm_voice_query}")
            
    elif service_option == "Both Services":
        st.markdown("### 🤝 Dual Service Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🤖 OpenAI Whisper")
            voice_query = create_voice_input_interface()
            if voice_query:
                st.info(f"OpenAI Result: {voice_query}")
        
        with col2:
            st.markdown("#### 🔵 IBM Watson")
            ibm_voice_query = create_ibm_voice_input_interface()
            if ibm_voice_query:
                st.info(f"IBM Result: {ibm_voice_query}")
                
    elif service_option == "Service Comparison":
        st.markdown("### 📊 Service Feature Comparison")
        compare_transcription_services()
        
        # Status checks
        col1, col2 = st.columns(2)
        with col1:
            display_voice_status()
        with col2:
            display_ibm_voice_status()


def sidebar_example():
    """Example of compact voice interfaces in sidebar."""
    with st.sidebar:
        st.markdown("### 🎤 Quick Voice Input")
        
        # Compact OpenAI interface
        st.markdown("**OpenAI Whisper:**")
        openai_result = create_compact_voice_interface()
        if openai_result:
            st.success(f"OpenAI: {openai_result}")
        
        # Compact IBM interface
        st.markdown("**IBM Watson:**")
        ibm_result = create_compact_ibm_voice_interface()
        if ibm_result:
            st.success(f"IBM: {ibm_result}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="Voice Input Demo",
        page_icon="🎤",
        layout="wide"
    )
    
    # Main demo
    main()
    
    # Sidebar demo
    sidebar_example()
