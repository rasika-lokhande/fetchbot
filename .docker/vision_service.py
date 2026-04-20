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

# Negative contrast prompts — what the robot sees when the object is NOT there
NEGATIVE_PROMPTS = [
    "a photo of an empty room",
    "a photo of furniture and walls",
]


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


def extract_text_input_from_request(request):
    if not request.json or 'text_input' not in request.json:
        raise ValueError('No text_input provided in request body')
    return request.json['text_input']


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


def build_prompts(text_input):
    """
    Build positive and negative prompts for open-ended detection.
    Uses contrast prompts so softmax is meaningful.

    Args:
        text_input: str — object or natural language query from LLM

    Returns:
        list[str]: [positive_prompt, *negative_prompts]
    """
    positive_prompt = f"a photo of a {text_input}"
    return [positive_prompt] + NEGATIVE_PROMPTS


def create_text_tokens(prompts):
    """
    Tokenize a list of prompts for CLIP.

    Args:
        prompts: list of str

    Returns:
        torch.Tensor: Tokenized text inputs on correct device
    """
    tokens = clip.tokenize(prompts).to(device)
    return tokens


def compute_clip_similarity(image_input, text_tokens):
    """
    Compute similarity scores between image and text prompts using CLIP.
    Softmax is applied across all prompts so scores are relative and meaningful.

    Args:
        image_input: Preprocessed image tensor
        text_tokens: Tokenized text tensor of shape (N, token_dim)

    Returns:
        torch.Tensor: Softmax similarity scores of shape (1, N)
    """
    with torch.no_grad():
        image_features = model.encode_image(image_input)
        text_features = model.encode_text(text_tokens)

        # Normalize features
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        # Softmax across all prompts — score is now meaningful relative to negatives
        similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)

    return similarity


def format_detections(text_input_str, similarity):
    """
    Extract the positive prompt confidence score from similarity scores.

    Args:
        text_input_str: Original text input string
        similarity: Softmax similarity tensor of shape (1, N)
                    Index 0 = positive prompt, rest = negative prompts

    Returns:
        dict: text_input, confidence (positive prompt score), detected (bool)
    """
    # Index 0 is always the positive prompt score
    confidence = float(similarity[0, 0].item())

    return {
        'text_input': text_input_str,
        'confidence': confidence
    }


@app.route('/detect', methods=['POST'])
def detect():
    """
    Detects objects in an image using CLIP with open-ended text prompts.

    Accepts:
    - image file (multipart/form-data)
    OR
    - base64 encoded image (JSON)

    AND
    - text_input: object name or natural language query (e.g. "green bottle", "I'm thirsty")

    Returns:
    - confidence: float — how likely the object is in the image (0-1)
    """
    try:
        # Step 1: Extract image and text input from request
        image = extract_image_from_request(request)
        text_input_str = extract_text_input_from_request(request)

        # Step 2: Preprocess image for CLIP
        image_input = preprocess_image(image)

        # Step 3: Build positive + negative prompts and tokenize
        prompts = build_prompts(text_input_str)
        text_tokens = create_text_tokens(prompts)

        # Step 4: Compute similarity scores across all prompts
        similarity = compute_clip_similarity(image_input, text_tokens)

        # Step 5: Extract positive prompt score and format result
        detection_result = format_detections(text_input_str, similarity)

        return jsonify({
            'success': True,
            'result': detection_result
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
        'device': device
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API info"""
    return jsonify({
        'service': 'FetchBot Vision Service',
        'endpoints': {
            '/health': 'GET - Health check',
            '/detect': 'POST - Detect objects in image'
        }
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)