from app.llama_manager import LlamaManager
from app.conversation_log import ConversationLog
from app.whisper_manager import WhisperManager
from app.speech_manager import SpeechManager
import threading
import pygame  # Add pygame for audio playback
import time
import re  # Add regular expressions import at the top
import openai
import os
from dotenv import load_dotenv
import queue  # Add queue for handling user input
import logging  # Optional: For logging in local.py

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


# 3. Prepare System Prompt with Call Description and Participants
def prepare_system_prompt(space_name, description, participants):
    prompt = f"Space Name: {space_name}\nDescription: {description}\nParticipants:\n"
    for participant in participants:
        prompt += f"- {participant['name']}: {participant['persona']}\n"
    
    # Add instructions and example for script-style responses
    prompt += (
        "Use the format: Name: Message (action: wait/interrupt [time to wait])\n\n"
        "Example:\n"
        "Alice: Hello, how are you? (action: wait)\n"
        "Bob: I'm doing well, thank you. Let's discuss AI advancements. (action: interrupt 3s)\n"
        "Carol: Sounds great! (action: interrupt 4s)\n"
        "Please continue the conversation by providing each AI participant's next response. "
        "For each response, include the participant's name followed by their message, "
        "and an action indicating whether they wait for others to speak or interrupt. "
    )
    # Include instructions to make the conversation natural and to decide when to wait or interrupt
    prompt += (
        "The conversation should feel natural, with participants politely waiting or "
        "interrupting when appropriate. Decide whether to wait or interrupt based on "
        "the flow of the conversation and any pauses. If the user hasn't spoken in a while, feel free to bring them back to the conversation.\n"
    )
    prompt += "\nConversation starts here.\n"
    return prompt

# 4. Simulate Conversation
def simulate_conversation(llama_manager, system_prompt, conversation_log, participants, whisper_manager):
    # Initialize pygame mixer for audio playback
    pygame.mixer.init()
    ai_audio_playing = False
    stop_playback = False
    interrupt_countdown = 0
    ai_speaking = False  # {{ Existing flag to track AI speaking state }}
    user_speaking = False  # {{ Added flag to track user speaking state }}

    # Initialize a thread-safe queue for user inputs
    user_input_queue = queue.Queue()

    # Function to continuously listen to the microphone and enqueue user inputs
    def listen_to_microphone():
        nonlocal user_speaking  # {{ Access the user_speaking flag }}
        while True:
            user_input = whisper_manager.record_and_transcribe_audio(duration=5)
            if user_input != "No speech detected.":
                user_speaking = True  # {{ Set flag when user starts speaking }}
                user_input_queue.put(user_input)
                logging.debug("User input queued.")
                user_speaking = False  # {{ Reset flag after capturing input }}

    # Start the microphone listener thread
    mic_thread = threading.Thread(target=listen_to_microphone, daemon=True)
    mic_thread.start()

    # Function to play AI audio
    def play_ai_audio(file_path, action=None, time_wait=0):
        nonlocal ai_audio_playing, stop_playback, interrupt_countdown, ai_speaking  # {{ Include ai_speaking
        if action == "interrupt":
            # Apply countdown before interrupting
            interrupt_countdown = int(time_wait.rstrip('s'))
            while interrupt_countdown > 0:
                print(f"Interrupting in {interrupt_countdown} seconds...")
                time.sleep(1)
                interrupt_countdown -= 1
            if ai_audio_playing:
                stop_playback = True
        ai_audio_playing = True
        ai_speaking = True  # {{ Set flag when AI starts speaking
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if stop_playback:
                pygame.mixer.music.stop()
                stop_playback = False
                break
            time.sleep(0.1)
        ai_audio_playing = False
        ai_speaking = False  # {{ Reset flag when AI stops speaking

    # Loop to maintain continuous conversation
    while True:
        try:
            # ➊ Check if there's new user input in the queue
            if not user_input_queue.empty():
                user_input = user_input_queue.get()
                logging.debug(f"Received user input: {user_input}")

                user_input = re.sub(r'[^\w\s]', '', user_input)
                logging.debug(f"Filtered user input: {user_input}")

                # ➋ If user is speaking, stop AI audio
                if ai_audio_playing:
                    stop_playback = True

                # {{ Check if user is not currently speaking }}
                if not user_speaking:
                    # ➌ Add user message to conversation log
                    conversation_log.add_message('You', user_input)

                    # Prepare input for LLaMA using LlamaManager
                    ai_responses = llama_manager.generate_response(
                        conversation_history=conversation_log.get_log(),
                        system_prompt=system_prompt,
                        participants=participants
                    )

                    # ➍ Add AI responses to conversation log and generate speech
                    for response in ai_responses:
                        if not response.get('content'):
                            continue  # Skip responses with empty content
                        conversation_log.add_message(response['name'], response['content'])
                        # Generate speech for AI response
                        speech_manager = setup_speech_manager()
                        voice = next((p['voice'] for p in participants if p['name'] == response['name']), 'alloy')
                        
                        # Ensure content is not empty before generating speech
                        if response['content'].strip():
                            try:
                                audio_file = speech_manager.text_to_speech(response['content'], voice)
                            except openai.BadRequestError as e:
                                print(f"Speech generation failed: {e}")
                                continue  # Skip this response if speech generation fails
                        else:
                            continue  # Skip if content is empty
                        
                        # Play the generated audio in a separate thread with action handling
                        if 'action' in response:
                            action = response['action']
                            time_wait = response.get('time', '0s')
                            playback_thread = threading.Thread(target=play_ai_audio, args=(audio_file, action, time_wait), daemon=True)
                        else:
                            playback_thread = threading.Thread(target=play_ai_audio, args=(audio_file,), daemon=True)
                        playback_thread.start()
                        
                        # {{ Clear user input queue after AI starts speaking }}
                        while not user_input_queue.empty():
                            user_input_queue.get()
                            logging.debug("User input cleared after AI started speaking.")

            # {{ If user begins speaking before AI speaks }}
            if user_speaking and not ai_audio_playing:
                user_input = user_input_queue.get()
                logging.debug(f"Received additional user input: {user_input}")

                user_input = re.sub(r'[^\w\s]', '', user_input)
                logging.debug(f"Filtered additional user input: {user_input}")

                # Add to conversation log and send to LLaMA model
                conversation_log.add_message('You', user_input)
                ai_responses = llama_manager.generate_response(
                    conversation_history=conversation_log.get_log(),
                    system_prompt=system_prompt,
                    participants=participants
                )

                # Add AI responses and handle speech
                for response in ai_responses:
                    if not response.get('content'):
                        continue
                    conversation_log.add_message(response['name'], response['content'])
                    # Generate speech for AI response
                    speech_manager = setup_speech_manager()
                    voice = next((p['voice'] for p in participants if p['name'] == response['name']), 'alloy')
                    
                    # Ensure content is not empty before generating speech
                    if response['content'].strip():
                        try:
                            audio_file = speech_manager.text_to_speech(response['content'], voice)
                        except openai.BadRequestError as e:
                            print(f"Speech generation failed: {e}")
                            continue  # Skip this response if speech generation fails
                    else:
                        continue  # Skip if content is empty
                    
                    # Play the generated audio in a separate thread with action handling
                    if 'action' in response:
                        action = response['action']
                        time_wait = response.get('time', '0s')
                        playback_thread = threading.Thread(target=play_ai_audio, args=(audio_file, action, time_wait), daemon=True)
                    else:
                        playback_thread = threading.Thread(target=play_ai_audio, args=(audio_file,), daemon=True)
                    playback_thread.start()
                    
                    # {{ Clear user input queue after AI starts speaking }}
                    while not user_input_queue.empty():
                        user_input_queue.get()
                        logging.debug("User input cleared after AI started speaking.")

            # ➏ Print the conversation so far
            print("\nCurrent Conversation:")
            for message in conversation_log.get_log():
                print(f"{message['name']}: {message['content']}")

        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, implement a short delay before continuing
            time.sleep(1)

        # Small delay before next interaction
        time.sleep(1)

def setup_speech_manager():
    speech_manager = SpeechManager(OPENAI_API_KEY)
    return speech_manager

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
        {'name': 'Alice', 'persona': 'An AI researcher specializing in machine learning algorithms.', 'voice': 'alloy'},
        {'name': 'Bob', 'persona': 'A tech journalist covering AI developments and trends.', 'voice': 'echo'},
        {'name': 'Carol', 'persona': 'An entrepreneur investing in AI startups.', 'voice': 'fable'}
    ]

    # Initialize LlamaManager
    llama_manager = LlamaManager()
    
    # Setup Whisper Manager
    whisper_manager = setup_whisper_manager()
    
    # Prepare system prompt
    system_prompt = prepare_system_prompt(space_name, description, participants)

    # Initialize conversation log
    conversation_log = ConversationLog()
    
    # Start the continuous conversation loop
    simulate_conversation(llama_manager, system_prompt, conversation_log, participants, whisper_manager)

if __name__ == "__main__":
    main()
