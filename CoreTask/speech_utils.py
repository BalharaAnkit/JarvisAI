import io
from gtts import gTTS
import pygame
import sys  # Import sys to check module context

# Initialize pygame mixer
pygame.mixer.init()

def speak(text, language="en", silent=False):
    """Convert text to speech and play it."""
    if 'gui' in sys.modules:  # Check if we're in the GUI context
        return  # Do nothing if we're running in GUI

    if not silent:
        print(f"Aria: {text}")  # Print what Aria says to the terminal

    # Create TTS object
    tts = gTTS(text=text, lang=language, slow=False)

    # Save TTS to an in-memory file
    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)

    # Load the in-memory file into pygame
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
