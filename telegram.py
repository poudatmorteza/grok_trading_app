from config import TG_API_KEY, TG_CHAT_ID
import requests

def send_message(message: str, parse_mode: str = None):
    url = f"https://api.telegram.org/bot{TG_API_KEY}/sendMessage"
    data = {
        "chat_id": TG_CHAT_ID,
        "text": message
    }
    
    # Only add parse_mode if it's provided
    if parse_mode:
        data["parse_mode"] = parse_mode
    
    response = requests.post(url, json=data)
    
    # If parsing fails, try sending as plain text
    if not response.json().get('ok', False):
        print(f"Parsing failed, sending as plain text: {response.json()}")
        data.pop("parse_mode", None)  # Remove parse_mode
        response = requests.post(url, json=data)
    
    return response.json()

def send_image(image_path: str):
    url = f"https://api.telegram.org/bot{TG_API_KEY}/sendPhoto"
    data = {
        "chat_id": TG_CHAT_ID
    }
    files = {
        "photo": open(image_path, "rb")
    }
    response = requests.post(url, data=data, files=files)
    return response.json()