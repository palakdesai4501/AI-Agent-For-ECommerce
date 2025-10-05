"""
Conversational Agent for E-Commerce Product Search

Unified AI agent that handles:
    1. General conversation (agent info, capabilities, shopping advice)
    2. Text-based product search (semantic similarity using RAG)
    3. Image-based product search (vision AI → semantic search)

The agent uses:
    - Google Gemini 2.0 for vision analysis and conversation
    - BAML for type-safe LLM function calls
    - Pinecone + sentence-transformers for semantic product search
    - SearchEngine for vector similarity search and product retrieval

Key Flow:
    User Input → HandleUserQuery (BAML) → Intent Classification
        ├─ GENERAL_CONVERSATION → Direct response
        ├─ PRODUCT_RECOMMENDATION → Text search → RAG response
        └─ IMAGE_SEARCH → Vision analysis → Query extraction → Text search → Results
"""

import os
import base64
from typing import Dict, List, Optional, Union
from PIL import Image
import io
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from baml_client import b
from src.search_engine import SearchEngine

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class ConversationalAgent:
    """
    Unified AI agent that handles general conversation, text-based product recommendations,
    and image-based product search for a commerce website.
    """
    
    def __init__(self):
        """Initialize the conversational agent with search capabilities."""
        data_path = os.path.join('data', 'processed_products.json')
        self.search_engine = None  # Lazy load
        self.data_path = data_path
        
        # Initialize Gemini for image analysis (lazy load)
        self.genai_configured = False
        self.vision_model = None
        
        # Agent identity
        self.agent_name = "Cartly"
        self.agent_description = "AI Shopping Assistant"
    
    def _ensure_search_engine(self):
        """Lazy load search engine to save memory."""
        if self.search_engine is None:
            from src.search_engine import SearchEngine
            self.search_engine = SearchEngine(self.data_path)
    
    def _ensure_vision_model(self):
        """Lazy load vision model to save memory."""
        if not self.genai_configured:
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.genai_configured = True
        if self.vision_model is None:
            self.vision_model = genai.GenerativeModel('gemini-2.0-flash-lite')
    
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
            # Ensure search engine is loaded
            self._ensure_search_engine()
            
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
            logger.info(f"Agent intent classified: {intent}")

            # Extract filters from BAML directive (price, rating, category)
            extracted_filters = {}
            if hasattr(directive, 'min_price') and directive.min_price:
                extracted_filters['min_price'] = directive.min_price
            if hasattr(directive, 'max_price') and directive.max_price:
                extracted_filters['max_price'] = directive.max_price
            if hasattr(directive, 'min_rating') and directive.min_rating:
                extracted_filters['min_rating'] = directive.min_rating
            if hasattr(directive, 'category') and directive.category:
                extracted_filters['category'] = directive.category

            # Merge with user-provided filters (user filters take precedence)
            merged_filters = {**extracted_filters, **(filters or {})}

            if merged_filters:
                logger.info(f"Applied filters: {merged_filters}")

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
                return self._handle_product_search(refined_query or message, merged_filters)

            # Image search
            if intent == "IMAGE_SEARCH":
                refined_query = directive.get("refined_query") if isinstance(directive, dict) else getattr(directive, "refined_query", None)
                # Pass image_description for simplification
                return self._handle_image_search(
                    image,
                    refined_query or image_description or message,
                    merged_filters,
                    image_description=image_description  # Pass description for query simplification
                )

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
        """Handle text-based product recommendations with RAG."""
        try:
            # Use existing search engine to retrieve products
            results = self.search_engine.search(
                message,
                filters=filters,
                top_k=3
            )

            # RAG: Pass retrieved products to LLM for intelligent response
            if results['results']:
                # Format retrieved products for context
                products_context = []
                for idx, product in enumerate(results['results'], 1):
                    context_item = f"{idx}. {product['title']}"
                    if product.get('description'):
                        context_item += f" - {product['description'][:200]}"
                    context_item += f" (Price: ${product.get('price', 0):.2f}, Rating: {product.get('rating', 0)}/5)"
                    products_context.append(context_item)

                products_text = "\n".join(products_context)

                # Generate context-aware response using RAG
                response_message = b.GenerateProductRecommendations(
                    user_query=message,
                    retrieved_products=products_text
                )
            else:
                # No products found - provide helpful alternative response
                response_message = self._generate_no_results_message(message, results.get('refined_query', message))

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
                           filters: Optional[Dict] = None,
                           image_description: Optional[str] = None) -> Dict:
        """Handle image-based product search."""
        try:
            search_query = None

            # Use provided image_description or analyze image
            if not image_description:
                image_data = self._prepare_image_for_analysis(image)
                image_description = self._analyze_image_content(image_data)

            logger.info("Image analyzed successfully")

            # Build semantic search query from image description
            # Extract key attributes and create a rich, semantic query
            product_type = self._extract_product_type(image_description) or "product"
            target_audience = self._extract_target_audience(image_description)
            category = self._extract_category(image_description)

            # Build query: product_type + target_audience + category (if relevant)
            query_parts = []
            if target_audience:
                query_parts.append(target_audience)
            query_parts.append(product_type)
            if category and category not in ['miscellaneous', 'general']:
                query_parts.append(category)

            search_query = ' '.join(query_parts)
            logger.info(f"Image search query generated: {search_query}")

            # Search with low threshold for better recall
            results = self.search_engine.search(
                search_query,
                filters=None,  # Don't apply filters for image search
                top_k=3,
                min_similarity=0.10  # Low threshold for image-based searches
            )
            logger.info(f"Image search returned {len(results.get('results', []))} products")

            if results['results']:
                # Generate simple message with actual count
                count = len(results['results'])
                if count == 1:
                    response_message = "I found 1 product for you."
                else:
                    response_message = f"I found {count} products for you."
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
            # Ensure vision model is loaded
            self._ensure_vision_model()

            # Prepare image for Gemini
            image_part = {
                "mime_type": "image/jpeg",
                "data": image_data
            }

            prompt = """
            Analyze this product image and extract key searchable attributes.

            Provide ONLY the following information in a structured format:
            - Product Type: (e.g., shirt, headphones, water bottle, etc.)
            - Category: (e.g., clothing, electronics, home goods, etc.)
            - Main Colors: (list 1-3 dominant colors)
            - Key Features: (list 2-4 distinctive visual features)
            - Material/Build: (if visible, e.g., cotton, plastic, metal, etc.)
            - Brand/Logo: (if visible)
            - Target Audience: (e.g., men, women, kids, unisex, etc.)

            Be specific and concise. Focus on attributes that would help find similar products in an e-commerce catalog.
            """

            response = self.vision_model.generate_content([prompt, image_part])
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error analyzing image with Gemini Vision: {e}")
            return "Product type: general item\nCategory: miscellaneous"

    def _extract_product_type(self, image_description: str) -> Optional[str]:
        """Extract just the product type from image description for fallback search."""
        try:
            # Parse the structured description (handles both "Product Type:" and "- Product Type:")
            for line in image_description.split('\n'):
                line_stripped = line.strip().lstrip('-').strip()
                if line_stripped.lower().startswith('product type:'):
                    product_type = line_stripped.split(':', 1)[1].strip()
                    return product_type
            return None
        except Exception:
            return None

    def _extract_category(self, image_description: str) -> Optional[str]:
        """Extract category from image description."""
        try:
            for line in image_description.split('\n'):
                line_stripped = line.strip().lstrip('-').strip()
                if line_stripped.lower().startswith('category:'):
                    category = line_stripped.split(':', 1)[1].strip()
                    return category
            return None
        except Exception:
            return None

    def _extract_target_audience(self, image_description: str) -> Optional[str]:
        """Extract target audience from image description."""
        try:
            for line in image_description.split('\n'):
                line_stripped = line.strip().lstrip('-').strip()
                if line_stripped.lower().startswith('target audience:'):
                    audience = line_stripped.split(':', 1)[1].strip().lower()
                    # Simplify audience terms
                    if 'women' in audience or 'female' in audience:
                        return "women's"
                    elif 'men' in audience or 'male' in audience:
                        return "men's"
                    elif 'kid' in audience or 'child' in audience:
                        return "kids"
            return None
        except Exception:
            return None

    def _simplify_image_query(self, image_description: str, baml_query: str) -> str:
        """
        Aggressively simplify image search query to maximize catalog matches.
        Removes colors, brands, and overly specific attributes.
        """
        # Extract key info from structured description
        product_type = None
        target_audience = None
        category = None

        for line in image_description.split('\n'):
            line_lower = line.lower()
            if line_lower.startswith('product type:'):
                product_type = line.split(':', 1)[1].strip()
            elif line_lower.startswith('target audience:'):
                target_audience = line.split(':', 1)[1].strip().lower()
            elif line_lower.startswith('category:'):
                category = line.split(':', 1)[1].strip().lower()

        # Build simplified query: [audience] + [product_type] + [category if relevant]
        query_parts = []

        # Add target audience if specified and relevant
        if target_audience and target_audience not in ['unisex', 'adults', 'general']:
            # Simplify audience terms
            if 'women' in target_audience or 'female' in target_audience:
                query_parts.append("women's")
            elif 'men' in target_audience or 'male' in target_audience:
                query_parts.append("men's")
            elif 'kid' in target_audience or 'child' in target_audience:
                query_parts.append("kids")

        # Add product type (REQUIRED)
        if product_type:
            # Remove brand names, colors, materials from product type
            product_clean = product_type.lower()
            # Remove common brand indicators
            for brand_word in ['nike', 'adidas', 'just so', 'apple', 'samsung', 'sony']:
                product_clean = product_clean.replace(brand_word, '')
            # Remove color words
            for color in ['black', 'white', 'red', 'blue', 'pink', 'coral', 'peach', 'gray', 'grey', 'green', 'yellow', 'purple']:
                product_clean = product_clean.replace(color, '')
            product_clean = ' '.join(product_clean.split())  # Remove extra spaces
            query_parts.append(product_clean)
        else:
            query_parts.append("product")

        # Add broad category hint if helpful
        if category and category in ['clothing', 'electronics', 'shoes', 'footwear']:
            if category == 'footwear':
                category = 'shoes'
            if category not in ' '.join(query_parts):
                query_parts.append(category)

        simplified = ' '.join(query_parts).strip()

        # Final cleanup: limit to 3-4 words max
        words = simplified.split()
        if len(words) > 4:
            simplified = ' '.join(words[:4])

        return simplified if simplified else "product"

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

    def _generate_no_results_message(self, original_query: str, refined_query: str) -> str:
        """Generate helpful message when no products are found."""
        # Get available categories to suggest
        available_categories = []
        if self.search_engine and hasattr(self.search_engine, 'get_category_suggestions'):
            available_categories = self.search_engine.get_category_suggestions()[:5]

        message = f"I couldn't find any products matching '{original_query}'. "

        # Add helpful suggestions
        if available_categories:
            message += f"However, I have products in these categories: {', '.join(available_categories)}. "

        message += "Try being more general (e.g., 'shirt' instead of 'red shirt'), or ask about a different product category."

        return message
    
    def get_agent_info(self) -> Dict:
        """Get information about the agent."""
        # Ensure search engine is loaded before accessing it
        self._ensure_search_engine()
        return {
            'name': self.agent_name,
            'description': self.agent_description,
            'capabilities': [
                'General conversation about shopping',
                'Text-based product recommendations',
                'Image-based product search',
                'Product comparison and explanations'
            ],
            'available_categories': self.search_engine.get_category_suggestions() if self.search_engine else [],
            'total_products': len(self.search_engine.products_data) if self.search_engine else 0
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