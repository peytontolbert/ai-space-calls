import torch
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from app.llama_manager import LlamaManager
from app.conversation_log import ConversationLog
from app.whisper_manager import WhisperManager


# 2. Setup Whisper Model for Speech-to-Text (Simulated)
def setup_whisper_model():
    # load model and processor
    processor = WhisperProcessor.from_pretrained("openai/whisper-small")
    model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
    model.config.forced_decoder_ids = None
    return model

# 3. Prepare System Prompt with Call Description and Participants
def prepare_system_prompt(space_name, description, participants):
    prompt = f"Space Name: {space_name}\nDescription: {description}\nParticipants:\n"
    for participant in participants:
        prompt += f"- {participant['name']}: {participant['persona']}\n"
    prompt += "\nConversation starts here.\n"
    return prompt

# 4. Simulate Conversation
def simulate_conversation(llama_manager, system_prompt, conversation_log, user_inputs, participants):
    for user_input in user_inputs:
        # Add user input to conversation log
        conversation_log.append({'name': 'You', 'content': user_input})

        # Prepare input for LLaMA using LlamaManager
        ai_responses = llama_manager.generate_response(
            conversation_history=conversation_log,
            system_prompt=system_prompt,
            participants=participants
        )

        # Add AI responses to conversation log
        for response in ai_responses:
            conversation_log.append({'name': response['name'], 'content': response['content']})

        # Print the conversation so far
        print("\nCurrent Conversation:")
        for message in conversation_log:
            print(f"{message['name']}: {message['content']}")

# 2. Setup Whisper Manager for Speech-to-Text
def setup_whisper_manager():
    whisper_manager = WhisperManager()
    return whisper_manager

# Main function to run the test
def main():
    # Example Call Description and Participants
    space_name = "AI Innovations Discussion"
    description = "A discussion about the latest advancements in artificial intelligence and their impact on society."
    participants = [
        {'name': 'Alice', 'persona': 'An AI researcher specializing in machine learning algorithms.'},
        {'name': 'Bob', 'persona': 'A tech journalist covering AI developments and trends.'},
        {'name': 'Carol', 'persona': 'An entrepreneur investing in AI startups.'}
    ]

    # Initialize LlamaManager
    llama_manager = LlamaManager()
    
    # Setup Whisper Manager
    whisper_manager = setup_whisper_manager()
    
    # Prepare system prompt
    system_prompt = prepare_system_prompt(space_name, description, participants)

    # Initialize conversation log
    conversation_log = ConversationLog()
    
    # Record audio and transcribe user input
    user_input = whisper_manager.record_and_transcribe_audio()
    conversation_log.append({'name': 'You', 'content': user_input})
    
    # Simulate the conversation
    simulate_conversation(llama_manager, system_prompt, conversation_log, [user_input], participants)

if __name__ == "__main__":
    main()
