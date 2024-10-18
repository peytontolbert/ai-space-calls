# AI Space Call

AI Space Call is a web application that allows users to create personalized space calls to engage in conversations with AI participants. It leverages advanced AI models like LLaMA for generating responses and Whisper for transcription.

## Features

- **Create Personalized Space Calls:** Define space name, description, and participants' personas.
- **Real-time Conversation:** Engage in conversations with AI-driven participants.
- **Audio Recording:** Capture and transcribe audio using Whisper.
- **AI Responses:** Generate dynamic responses from AI participants using LLaMA.
- **Microphone Controls:** Mute and unmute microphone during conversations.

## Getting Started

### Prerequisites

- **Python 3.7+**
- **pip** package manager

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/peytontolbert/ai-space-calls.git
    cd ai-space-calls
    ```

2. **Create a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Configuration

1. **Set environment variables:**

    - Create a `.env` file in the root directory (optional).
    - Add the following variables:

        ```
        SECRET_KEY=your_secret_key
        DEBUG=True
        ```

### Running the Application

1. **Start the Flask app:**

    ```bash
    python run.py
    ```

2. **Access the application:**

    Open your web browser and navigate to `http://localhost:5000`

## Usage

1. **Create a Space Call:**
    - Enter the space name and description.
    - Specify the number of AI participants (1-8).
    - Provide names and personas for each participant.

2. **Start the Conversation:**
    - Once the space is created, begin the conversation.
    - Use the microphone controls to mute/unmute as needed.
    - Engage with the AI participants through audio.

3. **End the Space:**
    - Click the "End Space" button to conclude the conversation.

## Project Structure

```
ai_space_call/
│
├── app/
│   ├── __init__.py
│   ├── routes.py           # Flask routes for UI interactions
│   ├── llama_manager.py    # Logic to manage LLaMA conversation
│   ├── whisper_manager.py  # Logic to handle Whisper transcription
│   ├── conversation_log.py # Manage conversation history
│   ├── templates/
│   │   └── index.html      # Frontend UI template
│   └── static/
│       └── style.css       # Optional styling for the UI
├── config.py               # Configuration file
├── run.py                  # Entry point to run the Flask app
└── requirements.txt        # Dependencies (Flask, transformers, etc.)
```

## Dependencies

- **Flask:** A lightweight WSGI web application framework.
- **Transformers:** State-of-the-art Natural Language Processing for Pytorch and TensorFlow 2.0.
- **Torch:** An open source machine learning framework.
- **Torchaudio:** Audio library for PyTorch.
- **Sounddevice:** Cross-platform audio library for Python.
- **Numpy:** Fundamental package for scientific computing with Python.
- **Recorder.js:** A JavaScript library for audio recording.
- **jQuery:** A fast, small, and feature-rich JavaScript library.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

