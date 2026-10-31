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

        system_prompt = data.get('systemPrompt')
        user_prompt = data.get('userPrompt')
        
        if not system_prompt or not user_prompt:
            return jsonify({'error': 'Missing prompts'}), 400

        # Check if user supplied their own custom API key from frontend
        user_api_key = request.headers.get('X-Gemini-API-Key')
        if user_api_key:
            client = genai.Client(api_key=user_api_key)
        else:
            client = default_client

        api_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=user_prompt,
            config={'system_instruction': system_prompt}
        )
        
        # Check if text exists safely
        if not api_response or not api_response.text:
            print("API Response blocked or empty:", api_response)
            return jsonify({'error': 'Model returned an empty response. Please check your prompt or safety settings.'}), 500

        return jsonify({'response': api_response.text})
        
    except Exception as e:
        err_msg = str(e)
        print("Backend Error:", err_msg)
        if '503' in err_msg or 'UNAVAILABLE' in err_msg:
            return jsonify({'error': 'The AI model is currently experiencing high demand. Please try again later or provide your own custom API key.'}), 503
        return jsonify({'error': err_msg}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)