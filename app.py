import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "X-Gemini-API-Key"])

default_client = genai.Client()

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400

        system_prompt = data.get('systemPrompt', '')
        user_prompt = data.get('userPrompt', '')
        
        if not user_prompt:
            return jsonify({'error': 'Missing user prompt'}), 400

        user_api_key = request.headers.get('X-Gemini-API-Key')
        if user_api_key and user_api_key.strip():
            current_client = genai.Client(api_key=user_api_key.strip())
        else:
            current_client = default_client

        full_prompt = f"System Instructions:\n{system_prompt}\n\nUser Task:\n{user_prompt}"

        api_response = current_client.models.generate_content(
            model='gemini-flash-latest',
            contents=full_prompt
        )
        
        response_text = ""
        if hasattr(api_response, 'text') and api_response.text:
            response_text = api_response.text
        elif api_response.candidates:
            for candidate in api_response.candidates:
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text

        if not response_text:
            return jsonify({'error': 'Model returned an empty response.'}), 500

        return jsonify({'response': response_text})

    except Exception as e:
        err_msg = str(e)
        print("Backend Error:", err_msg)
        return jsonify({'error': err_msg}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)