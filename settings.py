class Settings:
    SPEECH_SPEED_FACTOR = 1.0  # Lower value increases speech speed
    OPENAI_MODELS = ["gpt-4o-mini"] # "gpt-4o", "gpt-4o-turbo"
    MAX_WORDS = 150  # Maximum number of words in the AI response
    TRIGGER_WORD = "donald"
    TYPING_SPEED = 75  # Increase this value to slow down typing speed (milliseconds per character)
    FULLSCREEN_MODE = True  # Fullscreen on Raspberry Pi
    STATUS_FONT = ('Courier', 30, 'bold')
    USER_TEXT_FONT = ('Courier', 24)
    RESPONSE_TEXT_FONT = ('Courier', 28, 'bold')
    TTS_LANGUAGE = 'en'
    TTS_TLD = 'com'  # Top Level Domain (accent)