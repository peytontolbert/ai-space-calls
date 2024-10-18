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
        user_prompt = "\n".join([f"{msg['name']}: {msg['content']}" for msg in conversation_history[-20:]])
        prompt = system_prompt + "\n" + user_prompt
        
        # Generate a response from LLaMA
        outputs = self.pipe(
            prompt,
            max_new_tokens=1000,
        )
        generated_text = outputs[0]['generated_text']
        print(f"outputs: {outputs[0]['generated_text']}")
        # Begin parsing after "Conversation starts here."
        conversation_start = "Conversation starts here."
        start_index = generated_text.find(conversation_start)
        if start_index != -1:
            generated_text = generated_text[start_index + len(conversation_start):]
        ai_responses = self.parse_ai_response(generated_text, participants)
        return ai_responses

    def parse_ai_response(self, generated_text, participants):
        # Simple parsing logic; can be improved with regex or more advanced NLP
        lines = generated_text.strip().split('\n')
        ai_responses = []
        for line in lines:
            if line.startswith("You:"):
                continue  # Skip user lines
            if ':' in line:
                name, content = line.split(':', 1)
                name = name.strip()
                content = content.strip()
                # Parse action if present
                if '(' in content and ')' in content:
                    message, action_part = content.split('(', 1)
                    message = message.strip()
                    action_part = action_part.strip(')')
                    if action_part.startswith("action:"):
                        action_details = action_part[len("action:"):].strip()
                        if action_details.startswith("interrupt"):
                            parts = action_details.split()
                            action = "interrupt"
                            time_wait = parts[1] if len(parts) > 1 else "0s"
                            ai_responses.append({
                                'name': name,
                                'content': message,
                                'action': action,
                                'time': time_wait
                            })
                        else:
                            ai_responses.append({
                                'name': name,
                                'content': message,
                                'action': action_details
                            })
                    else:
                        ai_responses.append({'name': name, 'content': content})
                else:
                    ai_responses.append({'name': name, 'content': content})
        return ai_responses
