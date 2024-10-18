from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
import numpy as np

class WhisperManager:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

    def transcribe_audio(self, audio_input):
        # Audio input would be in some array form (already processed/streamed)
        input_features = self.processor(audio_input["array"], sampling_rate=audio_input["sampling_rate"], return_tensors="pt").input_features
        predicted_ids = self.model.generate(input_features)
        return self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

    def record_and_transcribe_audio(self, duration=5, sample_rate=16000):
        print("Recording audio...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()  # Wait until recording is finished
        print("Recording complete.")

        audio_input = {
            "array": audio.flatten(),
            "sampling_rate": sample_rate
        }
        transcription = self.transcribe_audio(audio_input)
        return transcription
