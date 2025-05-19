import requests
import os
import random

url = 'http://178.156.133.100:5000/upload/image'
image_folder_path = r'C:\Users\Nikhil\Pictures\Screenshots'

image_files = [f for f in os.listdir(image_folder_path) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
if not image_files:
    print("No image files found in the specified folder.")
else:
    image_path = os.path.join(image_folder_path, random.choice(image_files))

    with open(image_path, 'rb') as img:
        files = {'image': (image_path, img, 'image/png')}
        data = {'username': 'nikhil'}
        response = requests.post(url, files=files, data=data)

print("Status Code:", response.status_code)
print("Response:", response.text)
