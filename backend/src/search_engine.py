"""
Search Engine for E-Commerce Product Discovery

Combines vector similarity search with AI-powered recommendations to provide
intelligent product search functionality. Uses Pinecone for vector search and
BAML for LLM-based query refinement and product explanations.
"""

import json
import os
import logging
from typing import List, Dict, Optional
from src.vector_store import VectorStore
from baml_client import b

logger = logging.getLogger(__name__)

class SearchEngine:
    """
    Main search engine that combines vector search with AI-powered recommendations.
    """
    
    def __init__(self, products_data_file: str = "data/processed_products.json"):
        """
        Initialize search engine.
        
        Args:
            products_data_file: Path to processed products JSON file
        """
        self.products_data = {}
        self.vector_store = VectorStore()
        self._load_products_data(products_data_file)
    
    def _load_products_data(self, data_file: str):
        """Load full product data for detailed information."""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Create lookup dictionary by product ID
            for product in data['products']:
                self.products_data[product['id']] = product

            logger.info(f"Loaded detailed data for {len(self.products_data)} products")

        except FileNotFoundError:
            logger.error(f"Products data file not found: {data_file}")
        except Exception as e:
            logger.error(f"Error loading products data: {e}")
    
    def search(self,
               query: str,
               filters: Optional[Dict] = None,
               top_k: int = 10,
               min_similarity: float = 0.25) -> Dict:
        """
        Main search function that combines vector search with AI analysis.

        Args:
            query: User search query
            filters: Optional search filters
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (default 0.25, lower for image search)

        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Use refined query passed from entrypoint (already refined upstream)
            logger.info(f"Search query: '{query}'")
            refined_query = query

            # Build filters (support price_bucket if provided)
            pinecone_filters = filters or {}

            # Perform vector similarity search
            logger.debug("Performing vector similarity search...")
            similar_products = self.vector_store.search_similar_products(
                refined_query,
                top_k=top_k * 5,  # Get more candidates for better recall
                filters=pinecone_filters,
                min_similarity=min_similarity
            )
            logger.info(f"Vector search found {len(similar_products)} products (min_similarity={min_similarity})")
            
            if not similar_products:
                return {
                    'query': query,
                    'refined_query': refined_query,
                    'results': [],
                    'total_found': 0,
                    'message': 'No products found matching your search criteria.'
                }
            
            # Step 3: Enrich with full product data
            enriched_results = []
            for product_meta, similarity_score in similar_products:
                product_id = product_meta.get('product_id')

                if product_id and product_id in self.products_data:
                    full_product = self.products_data[product_id].copy()
                    full_product['similarity_score'] = similarity_score
                    # ensure image_url is present
                    if 'image_url' not in full_product and product_meta.get('image_url'):
                        full_product['image_url'] = product_meta.get('image_url')
                    enriched_results.append(full_product)
                else:
                    # Fallback: use metadata from vector store
                    fallback_product = {
                        'id': product_id or f"unknown_{len(enriched_results)}",
                        'title': product_meta['title'],
                        'category': product_meta['category'],
                        'store': product_meta.get('store'),
                        'price': product_meta['price'] if product_meta['price'] > 0 else None,
                        'rating': product_meta['rating'] if product_meta['rating'] > 0 else None,
                        'rating_count': product_meta['rating_count'],
                        'image_url': product_meta.get('image_url'),
                        'similarity_score': similarity_score,
                        'description': f"Product from {product_meta['category']} category"
                    }
                    enriched_results.append(fallback_product)
            
            # Return top K results
            final_results = enriched_results[:top_k]
            
            return {
                'query': query,
                'refined_query': refined_query,
                'results': final_results,
                'total_found': len(similar_products),
                'message': f'Found {len(final_results)} relevant products'
            }
            
        except Exception as e:
            logger.error(f"Search error: {e}", exc_info=True)
            return {
                'query': query,
                'results': [],
                'total_found': 0,
                'error': str(e),
                'message': 'Search encountered an error. Please try again.'
            }
    
    def get_product_explanation(self, product_id: str, user_query: str) -> str:
        """
        Get AI explanation for why a product is recommended.
        
        Args:
            product_id: ID of the product
            user_query: Original user query
            
        Returns:
            AI-generated explanation
        """
        try:
            if product_id not in self.products_data:
                return "Product information not available."
            
            product = self.products_data[product_id]
            product_info = json.dumps({
                'id': product.get('id'),
                'title': product.get('title'),
                'description': product.get('description', ''),
                'category': product.get('category'),
                'subcategories': product.get('subcategories', []),
                'price': product.get('price'),
                'rating': product.get('rating'),
                'rating_count': product.get('rating_count'),
                'store': product.get('store'),
                'image_url': product.get('image_url'),
                'features': product.get('features', [])[:5]
            }, indent=2)
            
            explanation = b.ExplainRecommendation(product_info, user_query)
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return "Unable to generate explanation for this product."
    
    def get_category_suggestions(self) -> List[str]:
        """
        Get list of available product categories.
        
        Returns:
            List of category names
        """
        categories = set()
        for product in self.products_data.values():
            if product['category']:
                categories.add(product['category'])
        return sorted(list(categories))