from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import base64
from PIL import Image
import io
from dotenv import load_dotenv
import requests
from src.conversational_agent import AgentAPI

load_dotenv()



app = Flask(__name__)

# Configurable CORS origins (comma-separated). Defaults to localhost for dev.
cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
CORS(app, origins=cors_origins)

# Initialize the agent
agent = AgentAPI()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from frontend."""
    try:
        data = request.json
        message = data.get('message', '')
        filters = data.get('filters', {})
        
        # Handle image if present
        image_data = data.get('image') or data.get('imageUrl')
        image_path = None
        
        if image_data:
            try:
                os.makedirs('temp', exist_ok=True)

                # Case 1: image is a data URL/base64
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    image_path = 'temp/uploaded_image.jpg'
                    image.save(image_path, 'JPEG')

                # Case 2: image is a remote URL
                elif isinstance(image_data, str) and image_data.startswith(('http://', 'https://')):
                    resp = requests.get(image_data, timeout=10)
                    resp.raise_for_status()
                    content = resp.content
                    # Try to open as image to validate and convert
                    image = Image.open(io.BytesIO(content))
                    image_path = 'temp/uploaded_image.jpg'
                    image.save(image_path, 'JPEG')

                # Case 3: assume raw base64 string
                else:
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    image_path = 'temp/uploaded_image.jpg'
                    image.save(image_path, 'JPEG')
                
            except Exception as e:
                return jsonify({'error': f'Image processing failed: {str(e)}'}), 400
        
        # Process with agent
        response = agent.chat(message, image_path, **filters)
        
        # Clean up temporary image
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/agent/info', methods=['GET'])
def agent_info():
    """Get agent information."""
    try:
        info = agent.get_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')