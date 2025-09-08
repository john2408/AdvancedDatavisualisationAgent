# 🔊 IBM Text-to-Speech Integration Guide

## Overview

This document describes the implementation of IBM Cloud Text-to-Speech functionality in the Advanced Data Visualization Agent, providing audio responses for assistant messages.

## 🏗️ Architecture

### Core Components

1. **IBMTextToSpeechSynthesizer Class** (`frontend/ibm_text_speech.py`)
   - Handles IBM Cloud TTS API communication
   - Manages authentication and audio synthesis
   - Provides error handling and logging

2. **Streamlit UI Components**
   - TTS control interface with enable/disable toggle
   - Voice selection dropdown with 6 IBM Watson voices
   - Status indicators and configuration display

3. **App Integration** (`app.py`)
   - Conditional audio generation for assistant responses
   - Seamless integration with existing chat interface
   - Session state management for TTS preferences

## 🔧 Setup and Configuration

### 1. Environment Variables

Set your IBM Text-to-Speech API key:

```bash
export IBM_TEXT_TO_SPEECH_KEY="your_api_key_here"
```

### 2. Configuration File

Verify the IBM TTS URL in `config.yaml`:

```yaml
ibm_text_to_speech_url: "https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/your_instance_id"
```

### 3. Dependencies

Required Python packages:
- `requests` - For IBM Cloud API communication
- `streamlit` - For UI components
- `omegaconf` - For configuration management
- `tempfile` - For audio file handling

## 🎤 Available Voices

IBM Watson provides 6 high-quality voices:

| Voice ID | Description | Use Case |
|----------|-------------|----------|
| `en-US_AllisonV3Voice` | Allison (US Female - Natural) | Default, conversational |
| `en-US_LisaV3Voice` | Lisa (US Female - Professional) | Business applications |
| `en-US_MichaelV3Voice` | Michael (US Male - Professional) | Formal presentations |
| `en-GB_KateV3Voice` | Kate (British Female) | International audience |
| `en-US_KevinV3Voice` | Kevin (US Male - Conversational) | Casual interactions |
| `en-US_OliviaV3Voice` | Olivia (US Female - Conversational) | Friendly dialogue |

## 🖥️ User Interface

### Sidebar Controls

The TTS functionality is accessible through the sidebar with these components:

1. **Enable Toggle**: Checkbox to activate/deactivate audio responses
2. **Voice Selection**: Dropdown to choose from available IBM voices
3. **Test Button**: Generate sample audio to preview selected voice
4. **Configuration Status**: Expandable section showing setup status

### Chat Integration

When TTS is enabled:
- Assistant messages automatically include audio playback
- Audio player appears below each assistant response
- Status caption indicates IBM Watson TTS usage

## 🔄 Implementation Flow

```
User Enables TTS
    ↓
Voice Selection
    ↓
Assistant Generates Response
    ↓
Text Preprocessing (remove markdown)
    ↓
IBM Watson TTS API Call
    ↓
Audio Bytes Returned
    ↓
Streamlit Audio Player
    ↓
User Hears Response
```

## 🛠️ Technical Details

### Authentication

Uses base64-encoded API key authentication:

```python
headers = {
    'Authorization': f'Basic {base64.b64encode(f"apikey:{api_key}".encode()).decode()}',
    'Content-Type': 'application/json',
    'Accept': 'audio/wav'
}
```

### Text Preprocessing

Assistant responses are cleaned before synthesis:
- Remove markdown formatting (`**`, `*`, `#`, `` ` ``)
- Limit text length to 1000 characters for performance
- Handle empty or invalid text inputs

### Error Handling

Comprehensive error handling for:
- Missing API credentials
- Network connectivity issues
- API rate limits and timeouts
- Invalid responses or audio data

### Audio Format

- **Format**: WAV (best Streamlit compatibility)
- **Quality**: Standard IBM Watson quality
- **Delivery**: Streamed directly to browser

## 📊 Performance Considerations

### Optimization Strategies

1. **Text Length Limiting**: Responses truncated to 1000 characters
2. **Conditional Generation**: Audio only generated when TTS enabled
3. **Error Resilience**: Graceful degradation when API unavailable
4. **Session Management**: TTS preferences persist across interactions

### API Usage

- **Cost**: Pay-per-character pricing from IBM
- **Limits**: Standard IBM Cloud rate limits apply
- **Latency**: ~1-3 seconds for typical responses

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_tts_functionality.py
```

Tests cover:
- Synthesizer initialization
- Voice configuration
- Response audio generation
- Text preprocessing
- App integration imports

## 🔍 Troubleshooting

### Common Issues

1. **No Audio Generated**
   - Check IBM_TEXT_TO_SPEECH_KEY environment variable
   - Verify config.yaml TTS URL
   - Ensure TTS is enabled in sidebar

2. **Authentication Errors**
   - Validate API key format and permissions
   - Check IBM Cloud service status
   - Verify service instance URL

3. **Audio Playback Issues**
   - Ensure browser supports WAV audio
   - Check network connectivity
   - Try different voice selection

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## 🚀 Usage Examples

### Basic TTS Activation

1. Open the application sidebar
2. Enable "Audio Responses" checkbox
3. Select preferred voice from dropdown
4. Click "Test Voice" to verify setup
5. Ask a question to hear audio response

### Voice Comparison

Test different voices:
1. Enable TTS
2. Select "Allison" voice
3. Click "Test Voice"
4. Switch to "Michael" voice
5. Click "Test Voice" again
6. Compare and choose preferred voice

### Integration with Existing Workflow

The TTS functionality integrates seamlessly:
1. Use voice input (IBM Watson or OpenAI)
2. Ask data visualization questions
3. Receive visual + audio responses
4. Continue conversation with audio feedback

## 🔮 Future Enhancements

Potential improvements:
- **Custom Voice Settings**: Speed, pitch, volume controls
- **Language Support**: Multi-language TTS capabilities
- **Audio Caching**: Store audio for repeated responses
- **Background Synthesis**: Pre-generate audio for common responses
- **Alternative TTS Providers**: Support for other TTS services

## 📚 Related Documentation

- [IBM Cloud Text-to-Speech API](https://cloud.ibm.com/docs/text-to-speech)
- [Streamlit Audio Components](https://docs.streamlit.io/library/api-reference/media/st.audio)
- [Advanced Data Visualization Agent Architecture](README.md)

## 🎯 Key Benefits

1. **Accessibility**: Support for visually impaired users
2. **Multitasking**: Listen while working on other tasks
3. **Professional Quality**: Enterprise-grade IBM Watson voices
4. **User Control**: Optional activation and voice selection
5. **Seamless Integration**: Works with existing chat interface
6. **Error Resilience**: Graceful handling of API issues

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Verify IBM Cloud service status
3. Review application logs for errors
4. Test with simple text inputs first
