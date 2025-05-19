import requests
import time

BASE_URL = "https://mia2.xyz/"  # change to your actual Flask server URL

def register(username, password):
    res = requests.post(f"{BASE_URL}/register", json={
        "username": username,
        "password": password
    })
    print("Register:", res.status_code, res.json())
    return res

def login(username, password):
    res = requests.post(f"{BASE_URL}/login", json={
        "username": username,
        "password": password
    })
    print("Login:", res.status_code, res.json())
    if res.status_code == 200:
        return res.json()["token"]
    return None

def update_username(token, new_username):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.post(f"{BASE_URL}/update-username", json={
        "new_username": new_username
    }, headers=headers)
    print("Update Username:", res.status_code, res.json())
    return res

if __name__ == "__main__":
    while True:
        print("\n--- User Flow ---")
        username = input("Enter username to register: ").strip()
        password = input("Enter password: ").strip()

        res = register(username, password)
        if res.status_code != 200:
            print("Registration failed, please try again.")
            continue
        time.sleep(1)

        token = login(username, password)
        if not token:
            continue

        new_username = input("Enter new username to update to: ").strip()
        time.sleep(1)
        update_username(token, new_username)

        again = input("\nTest another user? (y/n): ").strip().lower()
        if again != 'y':
            break
