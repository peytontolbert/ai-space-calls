from transformers import WhisperProcessor, WhisperForConditionalGeneration

class WhisperManager:
    def __init__(self):
        self.processor = WhisperProcessor.from_pretrained("openai/whisper-small")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

    def transcribe_audio(self, audio_input):
        # Audio input would be in some array form (already processed/streamed)
        input_features = self.processor(audio_input["array"], sampling_rate=audio_input["sampling_rate"], return_tensors="pt").input_features
        predicted_ids = self.model.generate(input_features)
        return self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
