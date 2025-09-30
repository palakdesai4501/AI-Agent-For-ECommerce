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
                 index_name: str = "amazon-products-test1",
                 dimension: int = 384,
                 metric: str = "cosine",
                 upsert_batch_size: int = 100,
                 embed_batch_size: int = 64):
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
        self.upsert_batch_size = upsert_batch_size
        self.embed_batch_size = embed_batch_size
        
        # Initialize embedding model
        print("Loading embedding model...")
        # Set cache directory and use token if available to avoid rate limits
        cache_dir = os.getenv('HF_HOME', '/tmp/huggingface_cache')
        os.makedirs(cache_dir, exist_ok=True)
        hf_token = os.getenv('HF_TOKEN')

        self.embedding_model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            cache_folder=cache_dir,
            token=hf_token
        )
        
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
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True, batch_size=self.embed_batch_size)
        return embeddings

    @staticmethod
    def _price_bucket(price: Optional[float]) -> int:
        """Compute coarse price bucket for filtering and sorting."""
        if price is None or price <= 0:
            return -1
        if price < 10:
            return 0
        if price < 25:
            return 1
        if price < 50:
            return 2
        if price < 100:
            return 3
        return 4

    def _build_views_for_product(self, product: Dict) -> List[Dict]:
        """
        Construct multiple short views per product to improve recall without heavy chunking.
        Returns a list of dicts: { 'id', 'text', 'metadata' }
        """
        product_id = product.get('id')
        title = product.get('title') or ''
        description = product.get('description') or ''
        category = product.get('category') or ''
        subcategories = product.get('subcategories') or []
        store = product.get('store') or ''
        price = product.get('price')
        rating = product.get('rating')
        rating_count = product.get('rating_count') or 0
        features = product.get('features') or []
        image_url = product.get('image_url') or ''

        taxonomy = " > ".join([category] + subcategories) if subcategories else category

        # View A: title + key features (short)
        view_a_text = "\n".join([
            f"Title: {title}",
            f"Brand/Store: {store}",
            f"Category: {taxonomy}",
            f"Key features: {', '.join(features[:6])}" if features else ""
        ]).strip()

        # View B: title + short description snippet
        desc_snippet = description[:600]
        view_b_text = "\n".join([
            f"Title: {title}",
            f"Use-case: {desc_snippet}"
        ]).strip()

        # Optionally view C from search_text if present
        search_text = product.get('search_text') or ''
        views: List[Dict] = []
        base_metadata = {
            'product_id': product_id,
            'view': '',
            'title': title[:200],
            'category': category,
            'subcategories': subcategories,
            'store': store[:100],
            'price': price if price is not None else 0.0,
            'price_bucket': self._price_bucket(price if isinstance(price, (int, float)) else None),
            'rating': rating if rating is not None else 0.0,
            'rating_count': rating_count,
            'image_url': image_url
        }

        views.append({
            'id': f"{product_id}#A",
            'text': view_a_text,
            'metadata': {**base_metadata, 'view': 'A'}
        })
        views.append({
            'id': f"{product_id}#B",
            'text': view_b_text,
            'metadata': {**base_metadata, 'view': 'B'}
        })

        if search_text:
            views.append({
                'id': f"{product_id}#C",
                'text': f"Semantic keywords: {search_text[:1000]}",
                'metadata': {**base_metadata, 'view': 'C'}
            })

        return views
    
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

            # Build views
            all_views: List[Dict] = []
            for product in products:
                all_views.extend(self._build_views_for_product(product))

            # Prepare embedding texts
            texts = [v['text'] for v in all_views]
            embeddings = self.create_embeddings(texts)

            vectors_to_upsert = []
            for view, embedding in zip(all_views, embeddings):
                vectors_to_upsert.append({
                    'id': view['id'],
                    'values': embedding.tolist(),
                    'metadata': view['metadata']
                })

            # Upsert in batches
            total = len(vectors_to_upsert)
            batch_size = self.upsert_batch_size
            for i in range(0, total, batch_size):
                batch = vectors_to_upsert[i:i + batch_size]
                self.index.upsert(vectors=batch)
                print(f"Upserted batch {i//batch_size + 1}/{(total - 1)//batch_size + 1}")
            
            # Wait for all upserts to complete
            time.sleep(5)
            
            # Verify the upsert
            stats = self.index.describe_index_stats()
            print(f"Index now contains {stats.get('total_vector_count', 'unknown')} vectors")
            
            return True
            
        except Exception as e:
            print(f"Error upserting products: {e}")
            return False
    
    def search_similar_products(self,
                              query: str,
                              top_k: int = 10,
                              filters: Optional[Dict] = None,
                              min_similarity: float = 0.3) -> List[Tuple[Dict, float]]:
        """
        Search for similar products using vector similarity.

        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional filters for metadata
            min_similarity: Minimum cosine similarity score (0-1), default 0.3

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
                if filters.get('price_bucket') is not None:
                    # allow single int or list
                    pb = filters['price_bucket']
                    if isinstance(pb, list):
                        pinecone_filter['price_bucket'] = {'$in': pb}
                    else:
                        pinecone_filter['price_bucket'] = {'$eq': pb}
            
            # Query Pinecone
            query_params = {
                'vector': query_embedding.tolist(),
                'top_k': top_k,
                'include_metadata': True
            }
            
            if pinecone_filter:
                query_params['filter'] = pinecone_filter
            
            results = self.index.query(**query_params)

            # Collapse by product_id and keep best scoring view
            best_by_product: Dict[str, Tuple[Dict, float]] = {}
            for match in results.get('matches', []):
                meta = match.get('metadata', {})
                pid = meta.get('product_id')
                score = match.get('score', 0.0)

                # Apply similarity threshold - skip products with low relevance
                if score < min_similarity:
                    continue

                if not pid:
                    # Fallback: try to build a synthetic id from title
                    pid = f"title::{meta.get('title', '')}"
                if pid not in best_by_product or score > best_by_product[pid][1]:
                    best_by_product[pid] = (meta, score)

            # Sort by score and take top_k unique products
            collapsed = sorted(best_by_product.values(), key=lambda x: x[1], reverse=True)[:top_k]

            # Log similarity scores for debugging
            if collapsed:
                print(f"📊 Top results with scores:")
                for i, (prod, score) in enumerate(collapsed[:5], 1):
                    print(f"   {i}. {prod.get('title', 'Unknown')[:50]} - Score: {score:.3f}")

            return collapsed
            
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