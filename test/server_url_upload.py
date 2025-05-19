import requests

url = 'https://mia2.xyz/upload/url'
post_url = 'https://www.reddit.com/r/Doom/s/tVSqQ1XNqM'

data = {'username': 'nik', 'url': post_url}
response = requests.post(url, data=data)

print("Status Code:", response.status_code)
print("Response:", response.text)
