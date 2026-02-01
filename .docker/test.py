
import base64
import requests
import json

# Read image and encode to base64
with open('.docker/blue_book.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Send POST request
response = requests.post(
    'http://localhost:5000/detect',
    json={'image': image_data}
)

# Pretty print response
print(json.dumps(response.json(), indent=2))
