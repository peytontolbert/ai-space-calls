from pathlib import Path
from openai import OpenAI
import time

"""
voices:
alloy
echo
fable
onyx
nova
shimmer
"""

class SpeechManager:
    def __init__(self, apikey):
        self.client = OpenAI(api_key=apikey)

    def text_to_speech(self, text, voice):
        # Save audio files to static/audio/ with a unique timestamp
        speech_file_path = Path(__file__).parent.parent / 'static' / 'audio' / f"{voice}_{int(time.time())}.mp3"
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path
