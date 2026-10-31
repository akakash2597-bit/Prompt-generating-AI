import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai

load_dotenv()
app = Flask(__name__)
CORS(app)

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

        # Check if user supplied their own custom API key
        user_api_key = request.headers.get('X-Gemini-API-Key')
        current_client = genai.Client(api_key=user_api_key) if user_api_key else default_client

        # Combine system instruction and user prompt cleanly
        full_contents = f"System Instructions: {system_prompt}\n\nUser Prompt: {user_prompt}"

        api_response = current_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=full_contents
        )
        
        if api_response and api_response.text:
            return jsonify({'response': api_response.text})
        else:
            return jsonify({'error': 'Model returned an empty response.'}), 500
    except Exception as e:
        err_msg = str(e)
        print("Backend Error:", err_msg)
        return jsonify({'error': err_msg}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)