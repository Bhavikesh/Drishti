import requests

def detect_language(text):
    """Simple language detection (check for Kannada Unicode range)"""
    # Kannada Unicode range: 0C80-0CFF
    for char in text:
        if '\u0C80' <= char <= '\u0CFF':
            return "kn"
    return "en"

def translate_to_english(text):
    """Google Translate free tier"""
    if detect_language(text) == "en":
        return text
    
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "kn",
        "tl": "en",
        "dt": "t",
        "q": text
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        return response.json()[0][0][0]
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_to_kannada(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": "kn",
        "dt": "t",
        "q": text
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        return response.json()[0][0][0]
    except Exception as e:
        print(f"Translation error: {e}")
        return text
