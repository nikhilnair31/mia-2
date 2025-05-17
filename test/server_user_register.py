import requests

url = 'http://178.156.133.100:5000/register'

while True:
    username = input("Enter a username to register (or 'exit' to quit): ").strip()
    if username.lower() == 'exit':
        break

    data = {'username': username}
    response = requests.post(url, json=data)

    print("Status Code:", response.status_code)
    print("Response:", response.text)