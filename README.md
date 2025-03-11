# AI Rubber Duck Debugging Assistant

This project is a modern, voice-controlled take on the classic rubber duck debugging technique. It creates an interactive AI rubber duck with a sarcastic personality that listens to your coding problems, responds with helpful technical advice, and keeps you entertained while debugging.


## 🦆 Features

- Voice-activated interaction - Say "Donald" to wake the duck, then ask your question
- Sarcastic AI personality with context-aware responses:
    - Technical help for debugging questions
    - Sarcasm for complaints
    - Encouragement for demoralized developers
- Text-to-speech responses synchronized with on-screen typing animation
- Matrix-themed GUI with animated rubber duck character
- Hands-free operation - perfect for debugging while coding


## 📋 Requirements
- Python 3.8+
- OpenAI API key
- Microphone for voice input
- Speakers for audio output
- Recommended: Raspberry Pi for dedicated hardware setup

## ⚙️ Installation
1. Clone this repository
```
git clone https://github.com/sayoung125/AIRubberDucky.git
cd AIRubberDucky
```

2. Create and activate a virtual environment (recommended)
```
python -m venv .venv
# On Windows
.\.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Download the Vosk speech recognition model (vosk-model-small-en-us-0.15)
```
# Create models directory if it doesn't exist
mkdir -p models
# Download and extract the model
cd models
# Download from https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
# Extract the zip file to models/vosk-model-small-en-us-0.15
```

5. Create a .env file in the project root with your OpenAI API key
```
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Usage
Run the application:
```
python AIProcessing.py
```
1. The matrix-themed GUI will launch with the animated duck
2. Say "Donald" to activate the listening mode
3. Ask your debugging question when prompted
4. The duck will respond both verbally and with text on screen
5. Say "Donald" again to ask another question

## 🔧 Configuration
### Customizing the AI Personality
You can modify the system prompt in AIProcessing.py to change the duck's personality:
```
self.system_prompt = """You are a sarcastic rubber duck debugging assistant. Your responses should be:
- Technical and helpful for debugging questions
- Sarcastic for complaints
- Inspirational for demoralized developers
Keep responses VERY brief (max 3-4 sentences) and entertaining."""
```

### Changing the Trigger Word
To use a different trigger word than "Donald", modify line 29 in AIProcessing.py:
```
trigger_word = "your_trigger_word"
```

### Adjusting Response Length
Modify the max_words attribute in the RubberDuckAI class:
```
self.max_words = 75  # Increase from default 50
```

## 🧩 Project Structure
- (file)AIProcessing.py - Main application logic, voice recognition, and AI interaction
- (file)AIDuckGUI.py - Matrix-themed GUI with animated duck
- (folder)models - Directory containing the Vosk speech recognition model
- (folder)duck - Duck animation graphics
- (file)requirements.txt - Python dependencies

## 🛠️ Technologies Used
- **OpenAI GPT-4o-mini** - AI language model for generating responses
- **Vosk** - Offline speech recognition
- **gTTS** (Google Text-to-Speech) - Voice synthesis
- **Tkinter** - GUI framework
- **Pygame** - Audio playback
- **Pillow** - Image processing for animations

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact
For questions or support, please open an issue on the GitHub repository.

*"Sometimes explaining your problem to a rubber duck is all you need... but a sarcastic AI duck is way more fun."*
