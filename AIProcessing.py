import threading
from openai import OpenAI, OpenAIError
from gtts import gTTS
import pygame
import io
import tempfile
import os
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import json
import queue
import tkinter as tk
from AIDuckGUI import RubberDuckGUI
from dotenv import load_dotenv

# Load environment variables at the top of the file
load_dotenv()

class RubberDuckMic:
    def __init__(self):
        # Load Vosk model
        self.model = Model("models/vosk-model-small-en-us-0.15")
        self.device_info = sd.query_devices(None, 'input')
        self.samplerate = int(self.device_info['default_samplerate'])
        self.q = queue.Queue()
        self.max_retries = 3

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(bytes(indata))

    def listen(self, gui=None):
        trigger_word = "donald"
        
        if gui:
            gui.root.after(0, gui.update_status, f"Say the trigger word: '{trigger_word.capitalize()}'")
        print(f"Say the trigger word: '{trigger_word.capitalize()}'")

        try:
            rec = KaldiRecognizer(self.model, self.samplerate)
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=8000,
                device=None,
                dtype='int16',
                channels=1,
                callback=self.callback
            ):
                while True:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip().lower()

                        # Only proceed when the trigger word is spoken
                        if trigger_word in text:
                            if gui:
                                gui.root.after(0, gui.update_status, "Ask your question now...")
                                # Start pulsing border
                                gui.root.after(0, gui.enable_listening_border)
                            print("Trigger word detected. Now listening for question.")
                            break

            # Second raw input stream for the actual question
            rec = KaldiRecognizer(self.model, self.samplerate)
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=8000,
                device=None,
                dtype='int16',
                channels=1,
                callback=self.callback
            ):
                while True:
                    data = self.q.get()
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        question_text = result.get("text", "").strip()
                        if question_text:
                            # Capitalize first letter
                            question_text = question_text[0].upper() + question_text[1:]
                            # Add question mark if not present
                            if not question_text.endswith("?"):
                                question_text += "?"
                            if gui:
                                gui.root.after(0, gui.update_status, "Processing...")
                                gui.root.after(0, gui.disable_listening_border)
                            print(f"You said: {question_text}")
                            return question_text

        except Exception as e:
            if gui:
                gui.root.after(0, gui.update_status, f"Error: {e}")
            print(f"Error during listening: {e}")
            return None

class RubberDuckTTS:
    def __init__(self):
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        # Default voice settings
        self.language = 'en'
        self.tld = 'com'  # Top Level Domain (accent)
        # Approximate words per minute for estimation
        self.wpm = 150
        
    def estimate_speech_duration(self, text):
        # Google TTS reads at approximately 150 words per minute
        word_count = len(text.split())
        # Calculate estimated duration in milliseconds
        estimated_duration = (word_count / self.wpm) * 60 * 1000
        # Add a buffer for pauses, punctuation, etc.
        return estimated_duration * 1.2  # 20% buffer

    def speak(self, text):
        try:
            # Start speaking in a separate thread
            thread = threading.Thread(target=self._speak_thread, args=(text,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"TTS Error: {e}")
            
    def _speak_thread(self, text):
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang=self.language, tld=self.tld, slow=False)
            
            mp3_data = io.BytesIO()
            tts.write_to_fp(mp3_data)
            mp3_data.seek(0)

            # Load from memory instead of a file
            pygame.mixer.music.load(mp3_data, "mp3")
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
        except Exception as e:
            print(f"TTS Thread Error: {e}")

class RubberDuckAI:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.tts = RubberDuckTTS()  # Add TTS instance
        self.system_prompt = """You are a sarcastic rubber duck debugging assistant. Your responses should be:
        - Technical and helpful for debugging questions
        - Sarcastic for complaints
        - Inspirational for demoralized developers
        Keep responses VERY brief (max 3-4 sentences) and entertaining."""
        self.max_words = 50  # Adjust this number as needed
        
    def truncate_response(self, text):
        words = text.split()
        if len(words) > self.max_words:
            return ' '.join(words[:self.max_words]) + "..."
        return text

    def process_and_respond(self, user_message, gui=None):
        # Get AI response
        ai_response = self.process_input(user_message)
        # Truncate response
        ai_response = self.truncate_response(ai_response)

        # Calculate appropriate typing speed if GUI is provided
        if gui:
            # Estimate speech duration
            duration = self.tts.estimate_speech_duration(ai_response)
            # Calculate characters per millisecond to match duration
            char_count = len(ai_response) + len("AI Rubber Duck: ")
            typing_speed = max(10, int(duration / char_count * 1.25))  # Minimum 10ms per char, increased by 5%
            # Set typing speed in GUI
            gui.typing_speed = typing_speed

        # Speak the response
        self.tts.speak(ai_response)
        return ai_response
    
    def process_input(self, user_message):
        o1_models = ["gpt-4o-mini", "gpt-4o"]
        try:
            response = self.client.chat.completions.create(
                model=o1_models[0],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,  # Adds some creativity to responses
                max_tokens=150  # Limits response length
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            return f"Quack! Error occurred: {e}"

def main():
    root = tk.Tk()
    gui = RubberDuckGUI(root)
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
        
    duck_ai = RubberDuckAI(api_key)
    mic = RubberDuckMic()
    
    def process_audio():
        while True:
            try:
                # Reset status to indicate ready
                root.after(0, gui.update_status, "")

                # Listen for input - pass GUI reference
                user_input = mic.listen(gui)

                if user_input:
                    root.after(0, gui.update_user_text, user_input)
                    root.after(0, gui.update_status, "")

                    response = duck_ai.process_and_respond(user_input, gui)
                
                    # Once AI response is generated, switch back to "Say Something"
                    root.after(0, gui.update_status, "")
                    root.after(0, gui.update_response_text, response)
                    
                if user_input and "exit" in user_input.lower():
                    root.quit()
                    break
                    
            except KeyboardInterrupt:
                root.quit()
                break
    
    # Start audio processing in a separate thread
    audio_thread = threading.Thread(target=process_audio)
    audio_thread.daemon = True
    audio_thread.start()
    
    # Start GUI main loop
    root.mainloop()

if __name__ == "__main__":
    main()