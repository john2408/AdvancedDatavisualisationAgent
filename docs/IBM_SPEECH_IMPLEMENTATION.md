# IBM Cloud Speech-to-Text Integration

## Overview
This module provides a complete implementation of IBM Cloud Speech-to-Text service for the Advanced Data Visualization Agent, offering an enterprise-grade alternative to OpenAI Whisper.

## Features

### 🎯 **Core Capabilities**
- **High-Accuracy Transcription**: IBM's enterprise-grade speech recognition
- **Confidence Scoring**: Receive quality metrics for each transcription
- **Real-Time Processing**: Fast audio-to-text conversion
- **Enterprise Security**: IBM Cloud's enterprise-grade privacy and security
- **Streamlit Integration**: Seamless UI components for voice input

### 🔧 **Technical Features**
- **Dynamic Audio Recording**: Using `streamlit-audio-recorder`
- **Session State Management**: Persistent transcription states
- **Error Handling**: Comprehensive error management and user feedback
- **API Rate Limiting**: Built-in timeout and connection error handling
- **Component Refresh**: Dynamic key generation for smooth UI updates

## Setup Instructions

### 1. **IBM Cloud Service Setup**
```bash
# 1. Create IBM Cloud account at https://cloud.ibm.com
# 2. Create Speech to Text service instance
# 3. Get your API key and service URL
# 4. Note your service region (e.g., au-syd, us-south, eu-gb)
```

### 2. **Environment Configuration**
```bash
# Set your IBM API key as environment variable
export IBM_SPEECH_TO_TEXT_KEY="your_ibm_api_key_here"

# Or add to your .env file
echo "IBM_SPEECH_TO_TEXT_KEY=your_ibm_api_key_here" >> .env
```

### 3. **Config File Setup**
Update `config.yaml` with your IBM service URL:
```yaml
ibm_speech_to_text_url: https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/your_instance_id
```

### 4. **Dependencies**
Ensure these packages are installed:
```bash
pip install streamlit
pip install streamlit-audio-recorder
pip install requests
pip install omegaconf
```

## Usage Examples

### Basic Implementation
```python
from frontend.ibm_speech_text import create_ibm_voice_input_interface

# In your Streamlit app
def main():
    st.title("Voice Input with IBM Watson")
    
    # Create IBM voice input interface
    voice_query = create_ibm_voice_input_interface()
    
    if voice_query:
        st.success(f"Transcribed: {voice_query}")
        # Process the voice query...
```

### Compact Interface
```python
from frontend.ibm_speech_text import create_compact_ibm_voice_interface

# For sidebar or smaller spaces
with st.sidebar:
    voice_input = create_compact_ibm_voice_interface()
    if voice_input:
        process_query(voice_input)
```

### Status Monitoring
```python
from frontend.ibm_speech_text import display_ibm_voice_status

# Display configuration status
display_ibm_voice_status()
```

### Service Comparison
```python
from frontend.ibm_speech_text import compare_transcription_services

# Show comparison between OpenAI and IBM
compare_transcription_services()
```

## API Reference

### `IBMVoiceTranscriber`
Main transcription class for IBM Cloud Speech-to-Text.

#### Methods:
- `__init__()`: Initialize with API credentials
- `transcribe_audio(audio_bytes: bytes) -> Optional[str]`: Transcribe audio data

#### Configuration:
- **Model**: `en-US_BroadbandModel` (optimized for clear speech)
- **Sample Rate**: 16000 Hz (optimal for speech recognition)
- **Audio Format**: WAV (best compatibility)
- **Timeout**: 30 seconds (prevents hanging requests)

### UI Components

#### `create_ibm_voice_input_interface() -> Optional[str]`
Full-featured voice input interface with:
- Audio recording widget
- Transcription button
- Transcript editing area
- Send/Clear/Re-record buttons

#### `create_compact_ibm_voice_interface() -> Optional[str]`
Compact interface for constrained spaces:
- Single-click recording and transcription
- Minimal UI footprint
- Automatic processing

#### `display_ibm_voice_status()`
Status dashboard showing:
- API key configuration status
- Service URL verification
- Feature capabilities
- Requirements checklist

## Configuration Details

### IBM Cloud Settings
The implementation uses specific IBM Cloud configurations:

```python
# API Configuration
headers = {
    'Authorization': f'Basic {base64.b64encode(f"apikey:{api_key}".encode()).decode()}',
    'Content-Type': 'audio/wav',
    'Accept': 'application/json'
}

# Recognition Parameters
params = {
    'model': 'en-US_BroadbandModel',    # English broadband model
    'content_type': 'audio/wav',         # Audio format
    'continuous': True,                  # Continuous recognition
    'interim_results': False,            # Only final results
    'max_alternatives': 1,               # Single best result
    'word_confidence': False,            # Disable word-level confidence
    'timestamps': False                  # Disable timestamps
}
```

### Session State Management
The implementation maintains state across Streamlit reruns:

```python
# Session state variables
- ibm_voice_transcriber: Transcriber instance
- ibm_audio_cleared: Audio clearing flag
- ibm_recording_counter: Component refresh counter
- ibm_voice_transcript: Current transcript
- ibm_compact_recording_counter: Compact interface counter
```

## Error Handling

### Common Errors and Solutions

#### ❌ **API Key Not Found**
```
Error: IBM_SPEECH_TO_TEXT_KEY environment variable not found!
Solution: Set the environment variable and restart the application
```

#### ❌ **Service URL Invalid**
```
Error: IBM Speech-to-Text URL not found in config!
Solution: Update config.yaml with correct service URL
```

#### ❌ **Connection Timeout**
```
Error: Request timed out. Please try again.
Solution: Check internet connection, try shorter audio clips
```

#### ❌ **Authorization Failed**
```
Error: IBM API error: 401 - Unauthorized
Solution: Verify API key is correct and service is active
```

## Performance Optimization

### Best Practices
1. **Audio Quality**: Use clear, noise-free recordings
2. **Duration**: Keep recordings under 1 minute for best performance
3. **Sample Rate**: 16000 Hz is optimal for speech recognition
4. **Network**: Ensure stable internet connection for API calls

### Monitoring
- Check transcription confidence scores
- Monitor API response times
- Track error rates for quality assurance

## Security Considerations

### Data Privacy
- Audio is transmitted securely to IBM Cloud via HTTPS
- No audio files are stored locally or permanently
- Transcripts are processed in memory only
- IBM Cloud enterprise privacy policies apply

### API Security
- API keys are base64 encoded for transmission
- Authentication uses IBM's standard API key format
- All requests use secure HTTPS connections

## Troubleshooting

### Debug Mode
Enable logging for detailed error information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues
1. **Microphone not working**: Check browser permissions
2. **No transcription**: Verify audio quality and speak clearly
3. **API errors**: Check credentials and service status
4. **UI not refreshing**: Clear browser cache and restart

## Comparison with OpenAI Whisper

| Feature | IBM Watson | OpenAI Whisper |
|---------|------------|----------------|
| **Accuracy** | Very High | Very High |
| **Speed** | Very Fast | Fast |
| **Languages** | Multiple | 100+ |
| **Confidence** | Yes | No |
| **Enterprise** | Yes | Standard |
| **Cost** | Variable | $0.006/min |

Choose IBM Watson for:
- Enterprise deployments
- Confidence scoring needs
- Clear speech environments
- IBM Cloud ecosystem integration

Choose OpenAI Whisper for:
- Multi-language support
- Noisy environments
- Simple pricing model
- Quick setup

---

**Ready to use enterprise-grade speech recognition in your visualization agent!** 🎤🔵
