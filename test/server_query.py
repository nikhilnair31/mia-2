import requests

url = 'https://mia2.xyz//query'
username = 'nikhil'
query_text = r'chat'

data = {'username': username, 'searchText': query_text}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.text)
