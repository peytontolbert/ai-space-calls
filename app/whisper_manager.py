from transformers import WhisperProcessor, WhisperForConditionalGeneration
import sounddevice as sd
import numpy as np
import logging  # Add logging for debugging
import threading  # Add threading for handling callbacks
import queue  # Add queue to communicate between threads
import collections  # {{ Added for buffering audio }}
import time  # {{ Added import for time handling }}

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class WhisperManager:
    def __init__(self, threshold=0.03):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
        self.threshold = 0.05  # {{ Increased threshold from 0.03 to 0.05 }}
        self.audio_queue = queue.Queue()  # {{ Queue to handle detected speech }}
        self.buffer = collections.deque()  # {{ Initialize a buffer to store audio chunks }}
        self.buffer_duration = 2  # seconds to keep in buffer
        self.sample_rate = 16000
        self.channels = 1
        self.is_buffering = False  # {{ Flag to indicate if buffering is active }}
        self.last_speech_time = None  # {{ Initialize last_speech_time for detecting silence duration }}
        self.silence_duration = 1.0  # {{ Required silence duration in seconds before ending speech }}

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

    def record_audio(self, audio_array, sample_rate=16000, channels=1):
        # {{ Modified to accept audio_array instead of recording internally }}
        try:
            logging.debug(f"Processing recorded audio: sample_rate={sample_rate}, channels={channels}")
            input_features = self.processor(audio_array, sampling_rate=sample_rate, return_tensors="pt").input_features
            predicted_ids = self.model.generate(input_features)
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            logging.debug(f"Transcription: {transcription}")
            return transcription
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            return "Transcription failed."

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            logging.warning(f"Sounddevice status: {status}")
        audio = indata.flatten()
        rms = np.sqrt(np.mean(audio**2))
        
        current_time = time.time()  # {{ Get current time }}

        if rms > self.threshold:
            if not self.is_buffering:
                logging.debug("Speech started, initiating buffering.")
                self.is_buffering = True
            self.buffer.append(audio.copy())
            self.last_speech_time = current_time  # {{ Update last_speech_time }}
        else:
            if self.is_buffering:
                if self.last_speech_time and (current_time - self.last_speech_time) > self.silence_duration:
                    logging.debug("Speech ended after 1 second of silence, processing buffered audio.")
                    self.is_buffering = False
                    full_audio = np.concatenate(list(self.buffer))
                    self.buffer.clear()
                    self.audio_queue.put(full_audio)

    def start_listening(self, sample_rate=16000, channels=1):
        self.stream = sd.InputStream(callback=self.audio_callback, samplerate=sample_rate, channels=channels)
        self.stream.start()
        logging.debug("Started audio stream for listening.")

    def stop_listening(self):
        self.stream.stop()
        self.stream.close()
        logging.debug("Stopped audio stream.")

    def get_transcription(self):
        if not self.audio_queue.empty():
            audio = self.audio_queue.get()
            return self.transcribe_audio({"array": audio, "sampling_rate": self.sample_rate})
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
