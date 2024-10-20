from flask import Blueprint, render_template, request, jsonify, url_for
from .llama_manager import LlamaManager
from .whisper_manager import WhisperManager
from config import Config
from .speech_manager import SpeechManager
from .conversation_log import ConversationLog
from .utils import prepare_system_prompt
import threading

main_bp = Blueprint('main', __name__)
config = Config()
# Initialize managers
llama_manager = LlamaManager(config.OPENAI_API_KEY)
whisper_manager = WhisperManager()
conversation_log = ConversationLog()
speech_manager = SpeechManager(config.OPENAI_API_KEY)
# Store user session data
user_sessions = {}

@main_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Extract form data
        space_name = request.form["space_name"]
        description = request.form["description"]
        num_participants = int(request.form["num_participants"])
        participants = []

        for i in range(1, num_participants + 1):
            name = request.form[f"participant_name_{i}"]
            persona = request.form[f"participant_description_{i}"]
            participants.append({"name": name, "persona": persona})

        # Initialize conversation log and system prompt
        system_prompt = prepare_system_prompt(space_name, description, participants)
        conversation_log.clear()
        conversation_log.set_system_prompt(system_prompt)

        # Store in user session
        user_sessions['system_prompt'] = system_prompt
        user_sessions['participants'] = participants

        return jsonify(success=True)
    return render_template("index.html")

@main_bp.route("/update_conversation", methods=["POST"])
def update_conversation():
    print("update_conversation called")
    # Get the audio data from the request
    audio_data = request.files.get('audio_data')
    if audio_data:
        # Process the audio data
        transcription = whisper_manager.transcribe_audio(audio_data)
        conversation_log.add_message('You', transcription)

        # Generate AI responses
        ai_responses = llama_manager.generate_response(
            conversation_log.get_log(),
            conversation_log.get_system_prompt(),
            user_sessions['participants']
        )

        updated_ai_responses = []
        for response in ai_responses:
            conversation_log.add_message(response['name'], response['content'])
            
            # Generate speech and get the audio file path
            audio_file = speech_manager.text_to_speech(response['content'], voice=response['voice'])
            
            # Create the URL for the audio file
            audio_url = url_for('static', filename=f'audio/{audio_file.name}')
            
            updated_ai_responses.append({
                'name': response['name'],
                'content': response['content'],
                'audio_url': audio_url
            })

        # Return the AI responses to the client
        return jsonify(ai_responses=updated_ai_responses)
    else:
        return jsonify(error="No audio data received"), 400
