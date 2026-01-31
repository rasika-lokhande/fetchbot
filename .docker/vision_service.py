from flask import Flask, request, jsonify
import torch
import clip
from PIL import Image
import io
import base64

app = Flask(__name__)

# Load CLIP model when container starts
print("Loading CLIP model...")
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
print(f"CLIP model loaded on {device}")

# Objects to detect
OBJECTS = [
    "red cup",
    "blue book", 
    "yellow ball",
    "green bottle"
]

# Confidence threshold for detection
CONFIDENCE_THRESHOLD = 0.3


def extract_image_from_request(request):
    """
    Extract image from POST request.
    Supports both file upload and base64 JSON formats.
    
    Returns:
        PIL.Image: RGB image
    Raises:
        ValueError: If no valid image found
    """
    if 'image' in request.files:
        # File upload format
        image_file = request.files['image']
        return Image.open(image_file.stream).convert('RGB')
    
    elif request.json and 'image' in request.json:
        # Base64 JSON format
        image_data = base64.b64decode(request.json['image'])
        return Image.open(io.BytesIO(image_data)).convert('RGB')
    
    else:
        raise ValueError('No image provided')


def preprocess_image(image):
    """
    Prepare image for CLIP model.
    
    Args:
        image: PIL Image
    
    Returns:
        torch.Tensor: Preprocessed image tensor on correct device
    """
    image_input = preprocess(image).unsqueeze(0).to(device)
    return image_input


def create_text_inputs(objects):
    """
    Create text prompts for CLIP from object names.
    
    Args:
        objects: List of object names (e.g., ["red cup", "blue book"])
    
    Returns:
        torch.Tensor: Tokenized text inputs on correct device
    """
    text_prompts = [f"a photo of a {obj}" for obj in objects]
    text_inputs = torch.cat([clip.tokenize(prompt) for prompt in text_prompts]).to(device)
    return text_inputs


def compute_clip_similarity(image_input, text_inputs):
    """
    Compute similarity scores between image and text using CLIP.
    
    Args:
        image_input: Preprocessed image tensor
        text_inputs: Tokenized text tensor
    
    Returns:
        torch.Tensor: Similarity scores (probabilities) for each text prompt
    """
    with torch.no_grad():
        # Encode image and text
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_inputs)
        
        # Normalize features
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)
        
        # Calculate similarity scores
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
    
    return similarity


def format_detections(similarity_scores, objects):
    """
    Format similarity scores into detection results.
    
    Args:
        similarity_scores: Tensor of similarity scores
        objects: List of object names
    
    Returns:
        list: Sorted list of detection dictionaries
    """
    detections = []
    for i, obj in enumerate(objects):
        confidence = float(similarity_scores[0, i].item())
        detections.append({
            'object': obj,
            'confidence': confidence
        })
    
    # Sort by confidence (highest first)
    detections.sort(key=lambda x: x['confidence'], reverse=True)
    return detections


def get_best_match(detections, threshold=CONFIDENCE_THRESHOLD):
    """
    Determine best matching object above confidence threshold.
    
    Args:
        detections: Sorted list of detection dictionaries
        threshold: Minimum confidence required
    
    Returns:
        str or None: Best matching object name, or None if below threshold
    """
    if detections and detections[0]['confidence'] > threshold:
        return detections[0]['object']
    return None


@app.route('/detect', methods=['POST'])
def detect():
    """
    Detects objects in an image using CLIP.
    
    Accepts:
    - image file (multipart/form-data)
    OR
    - base64 encoded image (JSON)
    
    Returns:
    - List of detected objects with confidence scores
    - Best match object
    """
    try:
        # Step 1: Extract image from request
        image = extract_image_from_request(request)
        
        # Step 2: Preprocess image for CLIP
        image_input = preprocess_image(image)
        
        # Step 3: Create text inputs
        text_inputs = create_text_inputs(OBJECTS)
        
        # Step 4: Compute similarity scores
        similarity = compute_clip_similarity(image_input, text_inputs)
        
        # Step 5: Format results
        detections = format_detections(similarity, OBJECTS)
        
        # Step 6: Determine best match
        best_match = get_best_match(detections)
        
        return jsonify({
            'success': True,
            'detections': detections,
            'best_match': best_match,
            'threshold': CONFIDENCE_THRESHOLD
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'CLIP ViT-B/32',
        'device': device,
        'objects': OBJECTS
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info"""
    return jsonify({
        'service': 'FetchBot Vision Service',
        'endpoints': {
            '/health': 'GET - Health check',
            '/detect': 'POST - Detect objects in image'
        },
        'objects': OBJECTS
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)