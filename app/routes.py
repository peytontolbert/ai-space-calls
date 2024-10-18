from flask import Blueprint, render_template, request, jsonify
from .llama_manager import LlamaManager
from .whisper_manager import WhisperManager
from .conversation_log import ConversationLog
from .utils import prepare_system_prompt
import threading

main_bp = Blueprint('main', __name__)

# Initialize managers
llama_manager = LlamaManager()
whisper_manager = WhisperManager()
conversation_log = ConversationLog()

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

        # Add AI responses to conversation log
        for response in ai_responses:
            conversation_log.add_message(response['name'], response['content'])

        # Return the AI responses to the client
        return jsonify(ai_responses=ai_responses)
    else:
        return jsonify(error="No audio data received"), 400
