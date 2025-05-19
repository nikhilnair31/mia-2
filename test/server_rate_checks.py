import requests
import time

URL = "https://mia2.xyz/hello"

# User-Agents to test blocking
user_agents = {
    "Normal Browser": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36",
    "Curl": "curl/7.68.0",
    "Python Requests": "python-requests/2.25.1",
    "Empty": "",
    "LegitScript": "Mozilla/5.0 (compatible; LegitScript/1.0)",
}

def test_user_agents():
    print("=== User-Agent Blocking Test ===")
    for label, ua in user_agents.items():
        try:
            headers = {"User-Agent": ua}
            response = requests.get(URL, headers=headers)
            print(f"{label}: Status {response.status_code}, Body: {response.text[:50]}")
        except Exception as e:
            print(f"{label}: Failed ({e})")

def test_rate_limiting():
    print("\n=== Rate Limiting Test ===")
    headers = {"User-Agent": user_agents["Normal Browser"]}  # Use a safe UA
    for i in range(10):
        try:
            response = requests.get(URL, headers=headers)
            print(f"Request {i + 1}: Status {response.status_code}, Body: {response.text[:50]}")
        except requests.exceptions.RequestException as e:
            print(f"Request {i + 1} failed: {e}")
        time.sleep(0.5)  # Send requests faster than the 1r/s limit to test

if __name__ == "__main__":
    test_user_agents()
    test_rate_limiting()