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

        user_api_key = request.headers.get('X-Gemini-API-Key')
        current_client = genai.Client(api_key=user_api_key) if user_api_key else default_client

        # Combine prompts to avoid SDK config version mismatches
        full_prompt = f"System Instructions:\n{system_prompt}\n\nUser Task:\n{user_prompt}"

        api_response = current_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=full_prompt
        )
        
        # Safe multi-way text extraction
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
            print("Full API Response Debug:", api_response)
            return jsonify({'error': 'Model returned an empty response. Try pasting your own API key.'}), 500

        return jsonify({'response': response_text})

    except Exception as e:
        err_msg = str(e)
        print("Backend Error:", err_msg)
        return jsonify({'error': err_msg}), 500