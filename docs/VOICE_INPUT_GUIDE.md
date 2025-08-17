# 🎤 Voice Input Feature Guide

## Overview
Your Visualization Agent now supports voice-to-text input using OpenAI Whisper for high-accuracy transcription.

## How to Use Voice Input

### 1. 🎙️ **Record Your Question**
- Click the **microphone button** in the sidebar
- Speak clearly into your microphone
- The recording will automatically stop after 2 seconds of silence
- You'll see a visual waveform while recording

### 2. 🔄 **Transcribe Audio**
- After recording, click **"🔄 Transcribe"** button
- Wait for OpenAI Whisper to process your audio
- The transcribed text will appear in the text area

### 3. ✏️ **Edit if Needed**
- Review the transcription for accuracy
- Edit the text in the text area if needed
- The transcription is usually very accurate for clear speech

### 4. 📤 **Send Your Query**
- Click **"📤 Send Query"** to submit your question
- The voice query will be processed like any typed question
- You'll get the same SQL generation and visualization

## Voice Query Examples

Try these sample voice queries:

### Basic Questions
- *"Show me the top 10 car manufacturers by registration volume"*
- *"Which electric vehicles were registered most in England?"*
- *"Compare BMW and Mercedes registration trends"*

### Time Series Analysis
- *"Plot monthly registration trends for Tesla from 2023 to 2024"*
- *"Show year over year growth for electric vehicles"*
- *"What are the quarterly patterns for luxury brands?"*

### Geographic Analysis
- *"Which regions prefer SUVs over sedans?"*
- *"Show electric vehicle adoption by district"*
- *"Compare London versus Manchester vehicle preferences"*

## Tips for Best Results

### 🎯 **Clear Speech**
- Speak clearly and at normal pace
- Avoid background noise when possible
- Use a good quality microphone if available

### 📱 **Browser Support**
- Works best in Chrome, Firefox, Safari, Edge
- Ensure microphone permissions are granted
- Works on both desktop and mobile devices

### 🌐 **Network Requirements**
- Requires internet connection for Whisper API
- Audio files are processed securely by OpenAI
- No audio is stored permanently

### 🔑 **Technical Requirements**
- OpenAI API key must be set as environment variable
- Modern web browser with microphone support
- Stable internet connection

## Troubleshooting

### ❌ **Voice Input Not Available**
- Check that `OPENAI_API_KEY` environment variable is set
- Restart the Streamlit application
- Verify your OpenAI account has API access

### 🎙️ **Recording Issues**
- Grant microphone permissions to your browser
- Check browser compatibility
- Try refreshing the page

### 🔄 **Transcription Errors**
- Speak more clearly and slowly
- Reduce background noise
- Try re-recording the audio
- Edit the transcript manually if needed

## Privacy & Security

- Audio is sent to OpenAI Whisper API for transcription
- No audio files are stored locally or permanently
- Transcripts are processed like regular text queries
- OpenAI's data usage policies apply

## Cost Considerations

- Voice transcription uses OpenAI Whisper API
- Costs approximately $0.006 per minute of audio
- Most queries are under 30 seconds (< $0.003 each)
- Very cost-effective for occasional use

---

**Enjoy hands-free querying of your vehicle registration database!** 🚗📊🎤
