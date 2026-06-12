import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

def query_mistral(prompt, system_prompt="You are Drishti, an AI assistant for Karnataka State Police. You help investigators analyze crime data and provide insights. Be professional, accurate, and helpful."):
    if not MISTRAL_API_KEY:
        print("Warning: MISTRAL_API_KEY not set. Using mock response.")
        return f"[Mock] Evaluated prompt: {prompt}"

    print(f"✓ Mistral API Key found (length: {len(MISTRAL_API_KEY)})")
    
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
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        print(f"→ Calling Mistral API with prompt length: {len(prompt)}")
        response = requests.post(MISTRAL_URL, headers=headers, json=data, timeout=30)
        print(f"← Mistral API responded with status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            print(f"✓ Successfully received response (length: {len(result)})")
            return result
        else:
            print(f"✗ Mistral API error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return f"I apologize, but I'm having trouble processing your request right now. Please try again."
            
    except requests.exceptions.Timeout:
        print("✗ Mistral API timeout")
        return "I apologize, but the request is taking too long. Please try again with a simpler question."
    except requests.exceptions.RequestException as e:
        print(f"✗ Mistral API request failed: {e}")
        return "I'm having trouble connecting to the AI service right now. Please try again in a moment."
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return "I encountered an unexpected error while processing your request."
