"""
app.py
-------
Flask backend for Bilingual Translation Web App.

This module exposes two endpoints:
1. /ping       — Simple health check.
2. /translate  — Accepts source language, target language, and text; returns translation via Microsoft Translator API.

Environment Variables Required:
- MICROSOFT_TRANSLATE_API_KEY
- MICROSOFT_TRANSLATE_REGION
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)
CORS(app) # Enable Cross-Origin Resource Sharing

# Load API key and region from environment variables
API_KEY = os.getenv("MICROSOFT_TRANSLATE_API_KEY")
REGION = os.getenv("MICROSOFT_TRANSLATE_REGION", "ukwest")


@app.route("/translate", methods=["POST"])
def translate_text():
    """
    POST /translate
    ----------------
    Translates a given text from a source language to a target language using Microsoft Translator API.

    Expects JSON body:
    {
        "source_lang": "en",
        "target_lang": "fr",
        "text": "Hello"
    }

    Returns JSON:
    {
        "translated_text": "Bonjour"
    }
    """
     # Extract request body
    data = request.get_json()
    source_lang = data.get("source_lang")
    target_lang = data.get("target_lang")
    text = data.get("text")

    # Ensure all required fields are present
    if not all([source_lang, target_lang, text]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Microsoft Translator API endpoint and config
    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    params = {
        "api-version": "3.0",
        "from": source_lang,
        "to": target_lang,
    }
    headers = {
        "Ocp-Apim-Subscription-Key": API_KEY,
        "Ocp-Apim-Subscription-Region": REGION,
        "Content-type": "application/json",
    }
    body = [{"text": text}]

     # Attempt translation request
    try:
        response = requests.post(endpoint, params=params, headers=headers, json=body)
        response.raise_for_status()
        translation = response.json()[0]["translations"][0]["text"]
        return jsonify({"translated_text": translation})
    except requests.exceptions.RequestException as e:
        print(e) # Log the exception for debugging
        return jsonify({"error": "Translation failed"}), 500

@app.route("/ping")
def ping():
    """
    GET /ping
    ---------
    Health check endpoint to confirm the backend is running.
    
    Returns JSON:
    {
        "message": "Flask backend is working!"
    }
    """
    return jsonify({"message": "Flask backend is working!"})

if __name__ == "__main__":
    # Start the Flask server on a dynamic or default port
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)