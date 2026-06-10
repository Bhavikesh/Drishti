import requests
import json
import os

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

def query_mistral(prompt, system_prompt="You are Drishti, an AI assistant for Karnataka State Police. Answer crime-related queries using only provided data. Be concise and professional."):
    if not MISTRAL_API_KEY:
        print("Warning: MISTRAL_API_KEY not set. Using mock response.")
        return f"[Mock] Evaluated prompt: {prompt}"

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistral-tiny",  # Free tier
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(MISTRAL_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error querying Mistral: {e}")
        return "I encountered an error while processing your request."
