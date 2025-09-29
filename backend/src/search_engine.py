import json
import os
from typing import List, Dict, Optional, Tuple
from src.vector_store import VectorStore
from baml_client import b
from baml_client.types import SearchFilters

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
                
            print(f"Loaded detailed data for {len(self.products_data)} products")
            
        except FileNotFoundError:
            print(f"❌ Products data file not found: {data_file}")
        except Exception as e:
            print(f"❌ Error loading products data: {e}")
    
    def search(self, 
               query: str, 
               filters: Optional[Dict] = None,
               top_k: int = 10,
               use_ai_reranking: bool = True) -> Dict:
        """
        Main search function that combines vector search with AI analysis.
        
        Args:
            query: User search query
            filters: Optional search filters
            top_k: Number of results to return
            use_ai_reranking: Whether to use AI for reranking results
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Step 1: Use refined query passed from entrypoint (already refined upstream)
            print(f"🔍 Using search query: '{query}'")
            refined_query = query
            print(f"📝 Refined query: '{refined_query}'")
            
            # Step 2: Build filters (support price_bucket if provided)
            pinecone_filters = filters or {}
            
            # Step 2b: Vector similarity search
            print("🔎 Performing vector similarity search...")
            similar_products = self.vector_store.search_similar_products(
                refined_query,
                top_k=top_k * 2,  # Get more results for AI filtering
                filters=pinecone_filters
            )
            print(f"🎯 Vector search found {len(similar_products)} similar products")
            
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
                        'price': product_meta['price'] if product_meta['price'] > 0 else None,
                        'rating': product_meta['rating'] if product_meta['rating'] > 0 else None,
                        'rating_count': product_meta['rating_count'],
                        'image_url': product_meta.get('image_url'),
                        'similarity_score': similarity_score,
                        'description': f"Product from {product_meta['category']} category"
                    }
                    enriched_results.append(fallback_product)
            
            # Step 4: AI-powered reranking and recommendations
            # Step 3b: Optionally AI rerank - disabled (handled upstream by intent refinement)
            final_results = enriched_results[:top_k]
            
            return {
                'query': query,
                'refined_query': refined_query,
                'results': final_results,
                'total_found': len(similar_products),
                'message': f'Found {len(final_results)} relevant products'
            }
            
        except Exception as e:
            print(f"❌ Search error: {e}")
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
            print(f"❌ Error generating explanation: {e}")
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
    
    def get_price_range(self, category: Optional[str] = None) -> Tuple[float, float]:
        """
        Get price range for products, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            Tuple of (min_price, max_price)
        """
        prices = []
        for product in self.products_data.values():
            if product['price'] is not None and product['price'] > 0:
                if category is None or product['category'] == category:
                    prices.append(product['price'])
        
        if prices:
            return (min(prices), max(prices))
        return (0.0, 1000.0)  # Default range
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Get search suggestions based on partial query.
        
        Args:
            partial_query: Partial search query
            
        Returns:
            List of suggested search terms
        """
        suggestions = set()
        partial_lower = partial_query.lower()
        
        # Look for matches in product titles and categories
        for product in self.products_data.values():
            title_words = product['title'].lower().split()
            for word in title_words:
                if word.startswith(partial_lower) and len(word) > len(partial_lower):
                    suggestions.add(word)
            
            if product['category'].lower().startswith(partial_lower):
                suggestions.add(product['category'])
        
        return sorted(list(suggestions))[:10]  # Return top 10 suggestions


class SearchFiltersHelper:
    """
    Helper class for managing search filters.
    """
    
    @staticmethod
    def create_filters(category: Optional[str] = None,
                      min_price: Optional[float] = None,
                      max_price: Optional[float] = None,
                      min_rating: Optional[float] = None) -> Optional[Dict]:
        """
        Create filters dictionary for search.
        
        Args:
            category: Product category filter
            min_price: Minimum price filter
            max_price: Maximum price filter
            min_rating: Minimum rating filter
            
        Returns:
            Filters dictionary or None if no filters
        """
        filters = {}
        
        if category and category != "All Categories":
            filters['category'] = category
        
        if min_price is not None and min_price > 0:
            filters['min_price'] = min_price
        
        if max_price is not None and max_price > 0:
            filters['max_price'] = max_price
        
        if min_rating is not None and min_rating > 0:
            filters['min_rating'] = min_rating
        
        return filters if filters else None
    
    @staticmethod
    def validate_filters(filters: Dict) -> Dict:
        """
        Validate and clean filters.
        
        Args:
            filters: Raw filters dictionary
            
        Returns:
            Validated filters dictionary
        """
        validated = {}
        
        if 'category' in filters and filters['category']:
            validated['category'] = str(filters['category']).strip()
        
        if 'min_price' in filters:
            try:
                min_price = float(filters['min_price'])
                if min_price >= 0:
                    validated['min_price'] = min_price
            except (ValueError, TypeError):
                pass
        
        if 'max_price' in filters:
            try:
                max_price = float(filters['max_price'])
                if max_price > 0:
                    validated['max_price'] = max_price
            except (ValueError, TypeError):
                pass
        
        if 'min_rating' in filters:
            try:
                min_rating = float(filters['min_rating'])
                if 0 <= min_rating <= 5:
                    validated['min_rating'] = min_rating
            except (ValueError, TypeError):
                pass
        
        # Ensure min_price <= max_price
        if 'min_price' in validated and 'max_price' in validated:
            if validated['min_price'] > validated['max_price']:
                validated['min_price'], validated['max_price'] = validated['max_price'], validated['min_price']
        
        return validated


# Example usage and testing
if __name__ == "__main__":
    print("🚀 Initializing Search Engine...")
    
    # Initialize search engine
    search_engine = SearchEngine()
    
    # Test search
    print("\n🔍 Testing search functionality...")
    
    test_queries = [
        "wireless bluetooth headphones",
        "kitchen knife set",
        "running shoes for women",
        "coffee maker under $100"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing: '{query}' ---")
        
        # Basic search
        results = search_engine.search(query, top_k=3)
        
        print(f"Query: {results['query']}")
        print(f"Refined: {results['refined_query']}")
        print(f"Found: {results['total_found']} products")
        print(f"Message: {results['message']}")
        
        for i, product in enumerate(results['results']):
            print(f"\n{i+1}. {product['title']}")
            print(f"   Category: {product['category']}")
            print(f"   Price: ${product['price']}" if product['price'] else "   Price: Not available")
            print(f"   Rating: ⭐ {product['rating']}/5.0 ({product['rating_count']} reviews)")
            print(f"   Similarity: {product.get('similarity_score', 0):.3f}")
            
            if 'ai_relevance_score' in product:
                print(f"   AI Relevance: {product['ai_relevance_score']}/100")
                print(f"   AI Reason: {product['ai_recommendation_reason']}")
    
    # Test categories
    print(f"\n📂 Available categories: {search_engine.get_category_suggestions()}")
    
    # Test price range
    min_price, max_price = search_engine.get_price_range()
    print(f"💰 Price range: ${min_price:.2f} - ${max_price:.2f}")
    
    print("\n✅ Search engine testing complete!")