import base64
import requests
import pytest

# Constants
URL = "http://localhost:5000/detect"
IMG_PATH = ".docker/test/test_images/red_cup.jpg"
text_input = "ball"

@pytest.fixture
def image_base64():
    """Encodes the test image to base64."""
    with open(IMG_PATH, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_health_check():
    """Confirm the container is up and model is loaded."""
    response = requests.get("http://localhost:5000/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'

def test_detection_success(image_base64):
    """Test the full detection flow via POST."""
    payload = {
        'image': image_base64, 
        'text_input': text_input
    }
    
    response = requests.post(URL, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'confidence' in data['result']
    print(data)

def test_missing_data_error():
    """Confirm the API returns 400 for bad requests."""
    response = requests.post(URL, json={'text_input': 'nothing'})
    assert response.status_code == 400
    assert response.json()['success'] is False