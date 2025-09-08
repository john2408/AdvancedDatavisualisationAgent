# 🎤 Voice Input Feature Guide

## Overview
Your Visualization Agent now supports voice-to-text input using both OpenAI Whisper and IBM Cloud Speech-to-Text for high-accuracy transcription. Choose between two enterprise-grade speech recognition services.

## How to Use Voice Input

### 🎙️ **Choose Your Service**
You can now use either:
- **OpenAI Whisper**: Global model with 100+ languages
- **IBM Cloud Speech-to-Text**: Enterprise-grade with confidence scoring

### 1. 🎙️ **Record Your Question**
- Click the **microphone button** in the sidebar
- Speak clearly into your microphone
- The recording will automatically stop after 2 seconds of silence
- You'll see a visual waveform while recording

### 2. 🔄 **Transcribe Audio**
**For OpenAI Whisper:**
- After recording, click **"🔄 Transcribe"** button
- Wait for OpenAI Whisper to process your audio

**For IBM Watson:**
- After recording, click **"🔄 Transcribe with IBM"** button
- Wait for IBM Cloud Speech-to-Text to process your audio
- You'll receive confidence scores for transcription quality

### 3. ✏️ **Edit if Needed**
- Review the transcription for accuracy
- Edit the text in the text area if needed
- Both services provide highly accurate transcriptions

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

**For OpenAI Whisper:**
- OpenAI API key must be set as environment variable: `OPENAI_API_KEY`
- Modern web browser with microphone support
- Stable internet connection

**For IBM Cloud Speech-to-Text:**
- IBM Speech-to-Text API key must be set as environment variable: `IBM_SPEECH_TO_TEXT_KEY`
- IBM service URL configured in `config.yaml`
- Modern web browser with microphone support
- Stable internet connection

## Troubleshooting

### ❌ **Voice Input Not Available**

**For OpenAI Whisper:**
- Check that `OPENAI_API_KEY` environment variable is set
- Restart the Streamlit application
- Verify your OpenAI account has API access

**For IBM Cloud Speech-to-Text:**
- Check that `IBM_SPEECH_TO_TEXT_KEY` environment variable is set
- Verify the IBM service URL in `config.yaml` is correct
- Ensure your IBM Cloud Speech-to-Text service is active
- Restart the Streamlit application

### 🎙️ **Recording Issues**
- Grant microphone permissions to your browser
- Check browser compatibility
- Try refreshing the page

### 🔄 **Transcription Errors**
- Speak more clearly and slowly
- Reduce background noise
- Try re-recording the audio
- Edit the transcript manually if needed
- Try the alternative transcription service

## Service Comparison

| Feature | OpenAI Whisper | IBM Cloud Speech-to-Text |
|---------|----------------|--------------------------|
| **Languages** | 100+ languages | Multiple languages |
| **Audio Quality** | Excellent with noise | Excellent for clear speech |
| **Speed** | Fast | Very fast |
| **Confidence Scores** | Not provided | Yes, provided |
| **Cost** | ~$0.006/minute | Variable pricing |
| **Privacy** | OpenAI policies | Enterprise-grade |
| **Best For** | Multilingual, noisy environments | Enterprise, clear speech |

## Privacy & Security

**OpenAI Whisper:**
- Audio is sent to OpenAI Whisper API for transcription
- No audio files are stored locally or permanently
- Transcripts are processed like regular text queries
- OpenAI's data usage policies apply

**IBM Cloud Speech-to-Text:**
- Audio is sent to IBM Cloud Speech-to-Text API for transcription
- Enterprise-grade security and privacy
- No audio files are stored locally or permanently
- Transcripts are processed like regular text queries
- IBM Cloud privacy policies apply

## Cost Considerations

**OpenAI Whisper:**
- Costs approximately $0.006 per minute of audio
- Most queries are under 30 seconds (< $0.003 each)
- Very cost-effective for occasional use

**IBM Cloud Speech-to-Text:**
- Variable pricing based on usage tier
- Enterprise plans available
- Free tier often available for development
- Cost-effective for enterprise use

---

**Enjoy hands-free querying of your vehicle registration database with dual transcription options!** 🚗📊🎤
