import os
import base64
from typing import Dict, List, Optional, Union
from PIL import Image
import io
from dotenv import load_dotenv
import google.generativeai as genai
from baml_client import b
from src.search_engine import SearchEngine

load_dotenv()
class ConversationalAgent:
    """
    Unified AI agent that handles general conversation, text-based product recommendations,
    and image-based product search for a commerce website.
    """
    
    def __init__(self):
        """Initialize the conversational agent with search capabilities."""
        # Use correct data path when running from backend directory
        import os
        data_path = os.path.join('..', 'data', 'processed_products.json')
        self.search_engine = SearchEngine(data_path)
        
        # Initialize Gemini for image analysis
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.vision_model = genai.GenerativeModel('gemini-2.0-flash-lite')
        
        # Agent identity
        self.agent_name = "Cartly"
        self.agent_description = "AI Shopping Assistant"
    
    def process_message(self, 
                       message: str, 
                       image: Optional[Union[str, bytes, Image.Image]] = None,
                       filters: Optional[Dict] = None) -> Dict:
        """
        Main entry point for all agent interactions.
        
        Args:
            message: User message text
            image: Optional image (file path, bytes, or PIL Image)
            filters: Optional search filters
            
        Returns:
            Dictionary with agent response
        """
        try:
            # Build single-entrypoint query for BAML
            has_image = image is not None
            image_description = None
            if has_image:
                try:
                    image_data = self._prepare_image_for_analysis(image)
                    image_description = self._analyze_image_content(image_data)
                except Exception:
                    image_description = "Product image provided"

            directive = b.HandleUserQuery({
                "user_message": message,
                "has_image": bool(has_image),
                "image_description": image_description
            })

            intent = directive.intent if isinstance(directive, dict) else getattr(directive, "intent", None)
            print(f"Agent Intent: {intent}")

            if intent == "GENERAL_CONVERSATION":
                reply = directive.get("reply") if isinstance(directive, dict) else getattr(directive, "reply", None)
                if reply:
                    return {
                        'type': 'conversation',
                        'message': reply,
                        'products': [],
                        'follow_up_questions': self._generate_conversation_followups(message),
                        'agent_name': self.agent_name
                    }
                # Fallback to pre-existing general conversation handler
                return self._handle_general_conversation(message)

            # Text product recommendation
            if intent == "PRODUCT_RECOMMENDATION":
                refined_query = directive.get("refined_query") if isinstance(directive, dict) else getattr(directive, "refined_query", None)
                return self._handle_product_search(refined_query or message, filters)

            # Image search
            if intent == "IMAGE_SEARCH":
                refined_query = directive.get("refined_query") if isinstance(directive, dict) else getattr(directive, "refined_query", None)
                return self._handle_image_search(image, refined_query or image_description or message, filters)

            # Fallback
            return self._handle_product_search(message, filters)
                
        except Exception as e:
            return {
                'type': 'error',
                'message': f"I encountered an error: {str(e)}. Please try again.",
                'products': [],
                'error': str(e)
            }
    
    def _handle_general_conversation(self, message: str) -> Dict:
        """Handle general conversation with the agent."""
        try:
            response = b.HandleGeneralConversation(message)
            
            # Add follow-up suggestions based on conversation
            follow_ups = self._generate_conversation_followups(message)
            
            return {
                'type': 'conversation',
                'message': response,
                'products': [],
                'follow_up_questions': follow_ups,
                'agent_name': self.agent_name
            }
        except Exception as e:
            return {
                'type': 'conversation',
                'message': f"Hi! I'm {self.agent_name}, your AI shopping assistant. I can help you find products, analyze images, or just chat about shopping. What would you like to do?",
                'products': [],
                'follow_up_questions': [
                    "What products are you looking for?",
                    "Upload an image to find similar products",
                    "What categories do you have?"
                ]
            }
    
    def _handle_product_search(self, message: str, filters: Optional[Dict] = None) -> Dict:
        """Handle text-based product recommendations."""
        try:
            # Use existing search engine
            results = self.search_engine.search(
                message,
                filters=filters,
                top_k=3,
                use_ai_reranking=True
            )

            if results['results']:
                # Format retrieved products for LLM context
                products_context = self._format_products_for_context(results['results'])

                # Use LLM to generate minimal response
                response_message = b.GenerateProductRecommendations(
                    user_query=message,
                    retrieved_products=products_context
                )
            else:
                response_message = "I couldn't find any products matching your request."

            return {
                'type': 'product_search',
                'message': response_message,
                'products': results['results'],
                'query_refined': results.get('refined_query', message),
                'total_found': results.get('total_found', 0),
                'follow_up_questions': self._generate_product_followups(message, results['results'])
            }

        except Exception as e:
            return {
                'type': 'error',
                'message': f"I had trouble searching for products. Please try again with different keywords.",
                'products': [],
                'error': str(e)
            }
    
    def _handle_image_search(self,
                           image: Union[str, bytes, Image.Image],
                           refined_hint: Optional[str] = None,
                           filters: Optional[Dict] = None) -> Dict:
        """Handle image-based product search."""
        try:
            image_description = None
            search_query = None

            if refined_hint:
                # We already have a refined query/description from the entrypoint
                search_query = refined_hint
            else:
                # Convert image to proper format for Gemini and analyze
                image_data = self._prepare_image_for_analysis(image)
                image_description = self._analyze_image_content(image_data)
                search_query = image_description

            print(f"Image analysis: {image_description}")
            print(f"Generated search query: {search_query}")

            # Search for similar products
            print(f"🔍 Searching for: '{search_query}'")
            results = self.search_engine.search(
                search_query,
                filters=filters,
                top_k=3,
                use_ai_reranking=False
            )
            print(f"📊 Search results: {len(results.get('results', []))} products found")

            if results['results']:
                # Format retrieved products for LLM context
                products_context = self._format_products_for_context(results['results'])

                # Use LLM to generate minimal response
                response_message = b.GenerateProductRecommendations(
                    user_query=f"Image search: {search_query}",
                    retrieved_products=products_context
                )
            else:
                response_message = "I couldn't find products similar to your image."

            return {
                'type': 'image_search',
                'message': response_message,
                'products': results['results'],
                'image_description': image_description,
                'search_query': search_query,
                'total_found': results.get('total_found', 0),
                'follow_up_questions': [
                    "Would you like to see more similar products?",
                    "Are you looking for a specific price range?",
                    "Do you need help with product details?"
                ]
            }

        except Exception as e:
            return {
                'type': 'error',
                'message': "I had trouble analyzing your image. Please try uploading a clear product image.",
                'products': [],
                'error': str(e)
            }
    
    def _prepare_image_for_analysis(self, image: Union[str, bytes, Image.Image]) -> bytes:
        """Prepare image data for Gemini Vision analysis."""
        if isinstance(image, str):
            # File path
            with open(image, 'rb') as f:
                return f.read()
        elif isinstance(image, bytes):
            # Raw bytes
            return image
        elif isinstance(image, Image.Image):
            # PIL Image
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            return buffer.getvalue()
        else:
            raise ValueError("Unsupported image format")
    
    def _analyze_image_content(self, image_data: bytes) -> str:
        """Analyze image content using Gemini Vision."""
        try:
            # Prepare image for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }
            
            prompt = """
            Analyze this image and describe the product shown. Focus on:
            1. Product type and category
            2. Color, style, and design features
            3. Material or build quality indicators
            4. Brand elements if visible
            5. Use case or target audience
            
            Provide a detailed but concise description suitable for product search.
            """
            
            response = self.vision_model.generate_content([prompt, image_part])
            return response.text.strip()
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return "A product image requiring similar item search"
    
    def _format_products_for_context(self, products: List[Dict]) -> str:
        """Format products into a structured context string for LLM analysis."""
        if not products:
            return "No products retrieved."

        context_parts = []
        for idx, product in enumerate(products, 1):
            product_info = f"""
Product {idx}:
- ID: {product.get('id', 'N/A')}
- Title: {product.get('title', 'N/A')}
- Category: {product.get('category', 'N/A')}
- Store/Brand: {product.get('store', 'N/A')}
- Price: ${product.get('price', 'N/A')}
- Rating: {product.get('rating', 'N/A')}/5.0 ({product.get('rating_count', 0)} reviews)
- Description: {product.get('description', 'N/A')[:300]}...
- Features: {', '.join(product.get('features', [])[:5]) if product.get('features') else 'None listed'}
- Similarity Score: {product.get('similarity_score', 0):.3f}
""".strip()
            context_parts.append(product_info)

        return "\n\n".join(context_parts)

    def _generate_conversation_followups(self, message: str) -> List[str]:
        """Generate follow-up questions for general conversation."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['name', 'who', 'what are you']):
            return [
                "What products are you shopping for today?",
                "Would you like to upload an image to find similar products?",
                "What categories interest you most?"
            ]
        elif any(word in message_lower for word in ['help', 'can you', 'what can']):
            return [
                "Try asking: 'Find me wireless headphones'",
                "Upload a product image for visual search",
                "Ask about specific categories like electronics or clothing"
            ]
        else:
            return [
                "What can I help you find today?",
                "Would you like product recommendations?",
                "Need help with a specific category?"
            ]
    
    def _generate_product_followups(self, query: str, products: List[Dict]) -> List[str]:
        """Generate follow-up questions for product searches."""
        if not products:
            return [
                "Try different keywords",
                "Upload an image of what you're looking for",
                "Ask about our available categories"
            ]
        
        categories = list(set(p.get('category', '') for p in products[:3]))
        
        followups = [
            f"Want to see more {categories[0]} products?" if categories else "See more similar products?",
            "Need help comparing these options?",
            "Looking for a specific price range?"
        ]
        
        return followups
    
    def get_agent_info(self) -> Dict:
        """Get information about the agent."""
        return {
            'name': self.agent_name,
            'description': self.agent_description,
            'capabilities': [
                'General conversation about shopping',
                'Text-based product recommendations',
                'Image-based product search',
                'Product comparison and explanations'
            ],
            'available_categories': self.search_engine.get_category_suggestions(),
            'total_products': len(self.search_engine.products_data)
        }
    
    def explain_product(self, product_id: str, user_query: str) -> str:
        """Get detailed explanation for a product recommendation."""
        return self.search_engine.get_product_explanation(product_id, user_query)


# Agent API for external use
class AgentAPI:
    """
    Simple API wrapper for the conversational agent.
    """
    
    def __init__(self):
        self.agent = ConversationalAgent()
    
    def chat(self, message: str, image_path: Optional[str] = None, **filters) -> Dict:
        """
        Chat with the agent.
        
        Args:
            message: User message
            image_path: Optional path to image file
            **filters: Optional search filters (category, min_price, max_price, min_rating)
            
        Returns:
            Agent response dictionary
        """
        # Convert filters
        search_filters = {}
        if 'category' in filters:
            search_filters['category'] = filters['category']
        if 'min_price' in filters:
            search_filters['min_price'] = float(filters['min_price'])
        if 'max_price' in filters:
            search_filters['max_price'] = float(filters['max_price'])
        if 'min_rating' in filters:
            search_filters['min_rating'] = float(filters['min_rating'])
        
        # Load image if provided
        image = None
        if image_path and os.path.exists(image_path):
            image = image_path
        
        # Optional price_bucket passthrough (int or list)
        if 'price_bucket' in filters:
            search_filters['price_bucket'] = filters['price_bucket']
        return self.agent.process_message(message, image, search_filters)
    
    def get_info(self) -> Dict:
        """Get agent information."""
        return self.agent.get_agent_info()
    
    def explain_product(self, product_id: str, query: str) -> str:
        """Get product explanation."""
        return self.agent.explain_product(product_id, query)


if __name__ == "__main__":
    # Test the conversational agent
    agent = ConversationalAgent()
    
    test_cases = [
        "What's your name?",
        "What can you do?",
        "Find me wireless headphones",
        "I need running shoes for women",
        "Recommend a coffee maker under $100"
    ]
    
    for query in test_cases:
        print(f"\n🗣️ User: {query}")
        response = agent.process_message(query)
        print(f"🤖 {response['message']}")
        if response.get('products'):
            print(f"   Found {len(response['products'])} products")
        if response.get('follow_up_questions'):
            print(f"   Suggestions: {response['follow_up_questions']}")