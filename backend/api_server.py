"""
Cartly E-Commerce API Server

Flask-based REST API that provides conversational AI shopping assistant capabilities.
Handles text-based product search, image-based product search, and general conversation.

Endpoints:
    POST /api/chat - Main chat endpoint for all interactions (text + image)
    GET /api/agent/info - Returns agent capabilities and catalog info
    GET /health - Health check endpoint for monitoring

Environment Variables:
    GEMINI_API_KEY - Google Gemini API key (required)
    PINECONE_API_KEY - Pinecone vector database API key (required)
    HF_TOKEN - HuggingFace token (optional, prevents rate limits)
    CORS_ORIGINS - Comma-separated allowed origins or "*" for all (default: "*")
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from PIL import Image
import io
from dotenv import load_dotenv
import requests
import logging
from src.conversational_agent import AgentAPI

# Load environment variables from .env file
load_dotenv()

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS based on environment variable
# Default is "*" for easy deployment, but can be restricted via CORS_ORIGINS env var
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
if cors_origins_env == "*":
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    logger.info("CORS configured to allow all origins")
else:
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    CORS(app, origins=cors_origins, supports_credentials=True)
    logger.info(f"CORS configured for origins: {cors_origins}")

# Initialize the conversational agent
# This loads the embedding model, vector store, and product data
agent = AgentAPI()
logger.info("Conversational agent initialized successfully")

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """
    Main chat endpoint for conversational AI interactions.

    Accepts:
        - Text queries for product search
        - Image uploads (base64 or URL) for visual product search
        - Optional filters (price range, rating, category)

    Request Body (JSON):
        {
            "message": "user query text",
            "image": "data:image/jpeg;base64,..." or "http://...",  // optional
            "filters": {  // optional
                "min_price": float,
                "max_price": float,
                "min_rating": float,
                "category": string
            }
        }

    Returns:
        JSON response with agent reply, products, and suggestions
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json
        message = data.get('message', '')
        filters = data.get('filters', {})

        # Process image if provided (supports base64 data URLs, remote URLs, or raw base64)
        image_data = data.get('image') or data.get('imageUrl')
        image_path = None

        if image_data:
            try:
                # Ensure temp directory exists for image storage
                os.makedirs('temp', exist_ok=True)

                # Case 1: Data URL format (e.g., "data:image/jpeg;base64,...")
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    logger.info("Processing data URL image")
                    image_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    image_path = 'temp/uploaded_image.jpg'
                    image.save(image_path, 'JPEG')

                # Case 2: Remote image URL
                elif isinstance(image_data, str) and image_data.startswith(('http://', 'https://')):
                    logger.info(f"Fetching remote image from URL")
                    resp = requests.get(image_data, timeout=10)
                    resp.raise_for_status()
                    content = resp.content
                    image = Image.open(io.BytesIO(content))
                    image_path = 'temp/uploaded_image.jpg'
                    image.save(image_path, 'JPEG')

                # Case 3: Raw base64 string
                else:
                    logger.info("Processing raw base64 image")
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    image_path = 'temp/uploaded_image.jpg'
                    image.save(image_path, 'JPEG')

            except Exception as e:
                logger.error(f"Image processing failed: {str(e)}")
                return jsonify({'error': f'Image processing failed: {str(e)}'}), 400

        # Process message with conversational agent
        logger.info(f"Processing chat request - Message length: {len(message)}, Has image: {image_path is not None}")
        response = agent.chat(message, image_path, **filters)

        # Clean up temporary image file
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.debug(f"Cleaned up temporary image: {image_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp image: {str(e)}")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent/info', methods=['GET'])
def agent_info():
    """
    Get agent capabilities and catalog information.

    Returns:
        JSON with agent name, description, capabilities, categories, and product count
    """
    try:
        info = agent.get_info()
        return jsonify(info)
    except Exception as e:
        logger.error(f"Agent info endpoint error: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        JSON with status: healthy
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Production deployment uses Gunicorn, so debug=False for safety
    # For local development, you can set debug=True
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, port=port, host='0.0.0.0')