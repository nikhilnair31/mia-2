import os
import json
import requests
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = 'token.json'
API_BASE = os.getenv('API_BASE', '')
APP_KEY = os.getenv('APP_KEY', '')

def register_user(username, password):
    resp = requests.post(f'{API_BASE}/register', json={'username': username, 'password': password})
    print(resp.json())

def login_user(username, password):
    resp = requests.post(f'{API_BASE}/login', json={'username': username, 'password': password})
    if resp.ok:
        token = resp.json().get('token')
        with open(TOKEN_FILE, 'w') as f:
            json.dump({'token': token}, f)
        return token
    else:
        print("Login failed:", resp.text)
        return None

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)['token']
    return None

def view_image(url, token):
    headers = {
        'Authorization': f'Bearer {token}',
        'User-Agent': 'buildmode',
        'X-App-Key': APP_KEY
    }
    resp = requests.get(url, headers=headers)
    if resp.ok:
        img = Image.open(BytesIO(resp.content))
        
        # Save to disk
        filename = os.path.basename(url)
        local_path = os.path.join('downloaded_images', filename)
        os.makedirs('downloaded_images', exist_ok=True)
        img.save(local_path)

        print(f"Image saved to {local_path}")
        img.show()
    else:
        print("Failed to fetch image:", resp.status_code, resp.text)

def main():
    token = load_token()
    if not token:
        username = input("Username: ")
        password = input("Password: ")
        register_user(username, password)  # Optional
        token = login_user(username, password)
        if not token:
            return

    url = input("Enter image URL: ")
    view_image(url, token)

if __name__ == '__main__':
    main()