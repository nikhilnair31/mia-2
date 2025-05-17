import requests

url = 'http://178.156.133.100:5000/query'
username = 'nikhil'
query_text = r'chat'

data = {'username': username, 'searchText': query_text}
response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.text)
