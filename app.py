# app.py

from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Setze hier deinen OpenAI API-Key und deine Assistant-ID
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Sicherer Weg über Umgebungsvariablen
ASSISTANT_ID = "asst_lRUX3sCqEr2kw5JRDNpcZg8y"

openai.api_key = OPENAI_API_KEY

@app.route('/', methods=['GET'])
def health_check():
    return "Server läuft!", 200

@app.route('/ask', methods=['POST'])
def ask_assistant():
    try:
        # Hole Text aus der Power Automate Anfrage
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Thread erstellen
        thread = openai.beta.threads.create()

        # Nachricht zum Thread hinzufügen
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Assistant antworten lassen
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Auf die Fertigstellung warten
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break

        # Antwort auslesen
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        assistant_reply = messages.data[0].content[0].text.value

        return jsonify({"reply": assistant_reply}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
