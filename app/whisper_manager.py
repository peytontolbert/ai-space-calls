from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
import numpy as np
import logging  # Add logging for debugging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WhisperManager:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

    def transcribe_audio(self, audio_input):
        try:
            # Audio input should be a NumPy array
            input_features = self.processor(audio_input["array"], sampling_rate=audio_input["sampling_rate"], return_tensors="pt").input_features
            predicted_ids = self.model.generate(input_features)
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            logging.debug(f"Transcription: {transcription}")
            return transcription
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            return "Transcription failed."

    def record_audio(self, duration=5, sample_rate=16000, channels=1):
        try:
            logging.debug(f"Recording audio: duration={duration}s, sample_rate={sample_rate}, channels={channels}")
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='float32')
            sd.wait()  # Wait until recording is finished
            logging.debug("Recording complete.")
            return {
                "array": audio.flatten(),
                "sampling_rate": sample_rate
            }
        except Exception as e:
            logging.error(f"Error during recording: {e}")
            return {
                "array": np.array([]),
                "sampling_rate": sample_rate
            }

    def record_and_transcribe_audio(self, duration=5, sample_rate=16000, channels=1, threshold=0.005):
        audio_input = self.record_audio(duration, sample_rate, channels)
        
        if self.is_user_speaking(audio_input["array"], threshold):
            transcription = self.transcribe_audio(audio_input)
            return transcription
        return "No speech detected."

    def is_user_speaking(self, audio_array, threshold=0.02):
        # Implement speech detection logic here
        # Calculate the Root Mean Square (RMS) to determine volume
        if audio_array.size == 0:
            logging.debug("Empty audio array received.")
            return False
        rms = np.sqrt(np.mean(audio_array**2))
        logging.debug(f"Audio RMS: {rms}, Threshold: {threshold}")
        return rms > threshold
