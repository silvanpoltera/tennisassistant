from flask import Flask, request, jsonify
import openai
import os
import time

app = Flask(__name__)

# API-Key und Assistant-ID aus Umgebungsvariablen
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = "asst_lRUX3sCqEr2kw5JRDNpcZg8y"
VECTOR_STORE_ID = "vs_680f75a3e1008191a4889758f2fc69f8"

openai.api_key = OPENAI_API_KEY

@app.route('/', methods=['GET'])
def health_check():
    return "Server läuft!", 200

@app.route('/ask', methods=['POST'])
def ask_assistant():
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Erstelle neuen Thread
        thread = openai.beta.threads.create()

        # Benutzeranfrage hinzufügen
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

        # Assistant ausführen mit Dokumentenbindung
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            tool_choice="required",
            tool_resources={
                "file_search": {
                    "vector_store_ids": [VECTOR_STORE_ID]
                }
            }
        )

        # Warten bis der Assistant fertig ist
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                return jsonify({"error": "Assistant run failed"}), 500
            time.sleep(1)

        # Letzte Antwort extrahieren
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:
            if msg.role == "assistant":
                reply = msg.content[0].text.value
                return jsonify({"reply": reply}), 200

        return jsonify({"error": "No assistant reply found"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
