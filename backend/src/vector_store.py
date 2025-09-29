import json
import os
from typing import List, Dict, Tuple, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import pinecone
from pinecone import Pinecone
import time

class VectorStore:
    """
    Handle vector embeddings and similarity search using Pinecone.
    """
    
    def __init__(self, 
                 index_name: str = "amazon-products-search",
                 dimension: int = 384,
                 metric: str = "cosine"):
        """
        Initialize vector store with Pinecone.
        
        Args:
            index_name: Name of the Pinecone index
            dimension: Vector dimension (384 for all-MiniLM-L6-v2)
            metric: Distance metric for similarity
        """
        self.index_name = index_name
        self.dimension = dimension
        self.metric = metric
        
        # Initialize embedding model
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Pinecone
        self.pc = None
        self.index = None
        self._init_pinecone()
        
    def _init_pinecone(self):
        """Initialize Pinecone client and index."""
        try:
            api_key = os.getenv('PINECONE_API_KEY')
            if not api_key:
                raise ValueError("PINECONE_API_KEY not found in environment variables")
            
            # Initialize Pinecone
            self.pc = Pinecone(api_key=api_key)
            
            # Check if index exists, create if not
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                print(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric=self.metric,
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
                # Wait for index to be ready
                time.sleep(10)
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            print(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {e}")
            raise
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings
        """
        print(f"Creating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def upsert_products(self, products: List[Dict]) -> bool:
        """
        Upsert products to Pinecone index.
        
        Args:
            products: List of product dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Upserting {len(products)} products to Pinecone...")
            
            # Extract search texts for embeddings
            search_texts = [product['search_text'] for product in products]
            
            # Create embeddings
            embeddings = self.create_embeddings(search_texts)
            
            # Prepare vectors for upsert
            vectors_to_upsert = []
            
            for i, (product, embedding) in enumerate(zip(products, embeddings)):
                # Create metadata (Pinecone has limits on metadata size)
                metadata = {
                    'title': product['title'][:200],  # Limit title length
                    'category': product['category'],
                    'price': product['price'] if product['price'] is not None else 0.0,
                    'rating': product['rating'] if product['rating'] is not None else 0.0,
                    'rating_count': product['rating_count'],
                    'store': product['store'][:100] if product['store'] else "",
                    'image_url': product['image_url'] if product['image_url'] else "",
                    'filename': product['filename']
                }
                
                vector = {
                    'id': product['id'],
                    'values': embedding.tolist(),
                    'metadata': metadata
                }
                
                vectors_to_upsert.append(vector)
            
            # Upsert in batches (Pinecone recommends batch size of 100)
            batch_size = 100
            for i in range(0, len(vectors_to_upsert), batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
            
            # Wait for all upserts to complete
            time.sleep(5)
            
            # Verify the upsert
            stats = self.index.describe_index_stats()
            print(f"Index now contains {stats['total_vector_count']} vectors")
            
            return True
            
        except Exception as e:
            print(f"Error upserting products: {e}")
            return False
    
    def search_similar_products(self, 
                              query: str, 
                              top_k: int = 10,
                              filters: Optional[Dict] = None) -> List[Tuple[Dict, float]]:
        """
        Search for similar products using vector similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional filters for metadata
            
        Returns:
            List of tuples (product_metadata, similarity_score)
        """
        try:
            # Create embedding for query
            query_embedding = self.embedding_model.encode([query])[0]
            
            # Prepare filter for Pinecone query
            pinecone_filter = {}
            if filters:
                if filters.get('category'):
                    pinecone_filter['category'] = {'$eq': filters['category']}
                if filters.get('min_price') is not None:
                    pinecone_filter['price'] = {'$gte': filters['min_price']}
                if filters.get('max_price') is not None:
                    if 'price' in pinecone_filter:
                        pinecone_filter['price']['$lte'] = filters['max_price']
                    else:
                        pinecone_filter['price'] = {'$lte': filters['max_price']}
                if filters.get('min_rating') is not None:
                    pinecone_filter['rating'] = {'$gte': filters['min_rating']}
            
            # Query Pinecone
            query_params = {
                'vector': query_embedding.tolist(),
                'top_k': top_k,
                'include_metadata': True
            }
            
            if pinecone_filter:
                query_params['filter'] = pinecone_filter
            
            results = self.index.query(**query_params)
            
            # Process results
            products_with_scores = []
            for match in results['matches']:
                product_data = match['metadata']
                similarity_score = match['score']
                products_with_scores.append((product_data, similarity_score))
            
            return products_with_scores
            
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """
        Get product by ID from Pinecone.
        
        Args:
            product_id: Product ID to fetch
            
        Returns:
            Product metadata if found, None otherwise
        """
        try:
            result = self.index.fetch(ids=[product_id])
            if product_id in result['vectors']:
                return result['vectors'][product_id]['metadata']
            return None
        except Exception as e:
            print(f"Error fetching product {product_id}: {e}")
            return None
    
    def get_index_stats(self) -> Dict:
        """
        Get Pinecone index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            return self.index.describe_index_stats()
        except Exception as e:
            print(f"Error getting index stats: {e}")
            return {}
    
    def clear_index(self) -> bool:
        """
        Clear all vectors from the index.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all vectors
            self.index.delete(delete_all=True)
            print("Index cleared successfully")
            return True
        except Exception as e:
            print(f"Error clearing index: {e}")
            return False


def setup_vector_store_from_data(data_file: str = "data/processed_products.json") -> VectorStore:
    """
    Set up vector store and populate with product data.
    
    Args:
        data_file: Path to processed products JSON file
        
    Returns:
        Initialized VectorStore instance
    """
    # Initialize vector store
    vector_store = VectorStore()
    
    # Load processed data
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data['products']
        print(f"Loaded {len(products)} products from {data_file}")
        
        # Check if index is empty
        stats = vector_store.get_index_stats()
        if stats.get('total_vector_count', 0) == 0:
            print("Index is empty, upserting products...")
            success = vector_store.upsert_products(products)
            if success:
                print("✅ Vector store setup complete!")
            else:
                print("❌ Failed to setup vector store")
        else:
            print(f"Index already contains {stats['total_vector_count']} vectors")
        
        return vector_store
        
    except FileNotFoundError:
        print(f"❌ Data file not found: {data_file}")
        print("Please run data processing first!")
        return vector_store
    except Exception as e:
        print(f"❌ Error setting up vector store: {e}")
        return vector_store


if __name__ == "__main__":
    # Test the vector store setup
    vector_store = setup_vector_store_from_data()
    
    # Test search
    if vector_store.index:
        print("\n🔍 Testing search...")
        results = vector_store.search_similar_products("wireless headphones", top_k=3)
        
        for i, (product, score) in enumerate(results):
            print(f"\n{i+1}. {product['title']} (Score: {score:.3f})")
            print(f"   Category: {product['category']}")
            print(f"   Price: ${product['price']}" if product['price'] > 0 else "   Price: Not available")
            print(f"   Rating: {product['rating']}/5.0 ({product['rating_count']} reviews)")