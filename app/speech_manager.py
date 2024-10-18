from pathlib import Path
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI

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
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def text_to_speech(self, text, voice):
        speech_file_path = Path(__file__).parent / f"{voice}.mp3"
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(speech_file_path)
        return speech_file_path
