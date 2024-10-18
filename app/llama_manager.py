from transformers import pipeline

class LlamaManager:
    def __init__(self):
        self.model_id = "meta-llama/Llama-3.2-3B-Instruct"
        self.pipe = pipeline(
            "text-generation",
            model=self.model_id,
            torch_dtype="bfloat16",
            device_map="auto",
            max_new_tokens=5000
        )
    def generate_response(self, conversation_history, system_prompt, participants):
        # Prepare user input with the last 20 messages from conversation history
        user_prompt = ""
        for message in conversation_history[-20:]:
            user_prompt += f"{message['role']}: {message['content']}\n"
        
        # Generate a response from LLaMA
        outputs = self.pipe(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            max_new_tokens=256,
        )
        generated_text = outputs[0]['generated_text']

        # Parse the generated text to extract the next speaker and their response
        # Assuming the model outputs in the format "Name: Message"
        ai_responses = self.parse_ai_response(generated_text, participants)

        return ai_responses

    def parse_ai_response(self, generated_text, participants):
        # Simple parsing logic; can be improved with regex or more advanced NLP
        lines = generated_text.strip().split('\n')
        ai_responses = []
        for line in lines:
            if ':' in line:
                name, content = line.split(':', 1)
                name = name.strip()
                content = content.strip()
                if any(p['name'] == name for p in participants):
                    ai_responses.append({'name': name, 'content': content})
        return ai_responses