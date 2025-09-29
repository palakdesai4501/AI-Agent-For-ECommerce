import json
import pandas as pd
from datasets import load_dataset
from typing import List, Dict, Optional
import os
from datetime import datetime

class AmazonDataProcessor:
    """
    Process Amazon Products 2023 dataset intelligently.
    Focus on key e-commerce categories and limit to 500-1000 products.
    """
    
    # Most important e-commerce categories for general consumers
    PRIORITY_CATEGORIES = [
        'meta_Electronics',
        'meta_Home_and_Kitchen', 
        'meta_Clothing_Shoes_and_Jewelry',
        'meta_Beauty_and_Personal_Care',
        'meta_Sports_and_Outdoors',
        'meta_Health_and_Household',
        'meta_Office_Products',
        'meta_Pet_Supplies'
    ]
    
    def __init__(self, target_size: int = 800):
        """
        Initialize processor with target dataset size.
        
        Args:
            target_size: Target number of products (500-1000 recommended)
        """
        self.target_size = target_size
        self.processed_data = []
        
    def load_and_filter_data(self) -> List[Dict]:
        """
        Load dataset and intelligently filter to target size.
        
        Returns:
            List of processed product dictionaries
        """
        print("Loading Amazon Products 2023 dataset...")
        
        try:
            # Load the dataset
            ds = load_dataset("milistu/AMAZON-Products-2023")
            df = ds['train'].to_pandas()
            
            print(f"Original dataset size: {len(df)} products")
            
            # Filter by priority categories
            priority_products = df[df['filename'].isin(self.PRIORITY_CATEGORIES)]
            
            print(f"Priority categories contain: {len(priority_products)} products")
            
            # Further filtering for quality and completeness
            filtered_df = self._apply_quality_filters(priority_products)
            
            # Sample to target size if needed
            if len(filtered_df) > self.target_size:
                # Stratified sampling to maintain category distribution
                sampled_df = self._stratified_sample(filtered_df)
            else:
                sampled_df = filtered_df
                
            print(f"Final dataset size: {len(sampled_df)} products")
            
            # Process the data
            self.processed_data = self._process_products(sampled_df)
            
            return self.processed_data
            
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return []
    
    def _apply_quality_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply quality filters to ensure good product data.
        
        Args:
            df: DataFrame to filter
            
        Returns:
            Filtered DataFrame
        """
        # Filter criteria for quality products
        filtered = df[
            # Must have title and description
            (df['title'].notna()) & 
            (df['description'].notna()) &
            (df['title'].str.len() > 10) &
            (df['description'].str.len() > 20) &
            
            # Must have some rating data (indicates real products)
            (df['rating_number'].notna()) &
            (df['rating_number'] > 0) &
            (df['average_rating'].notna()) &
            
            # Must have main category
            (df['main_category'].notna()) &
            
            # Must have image
            (df['image'].notna()) &
            
            # Filter out products with very low ratings (likely problematic)
            (df['average_rating'] >= 3.0)
        ].copy()
        
        # Sort by rating quality (number of ratings * average rating)
        filtered['quality_score'] = filtered['rating_number'] * filtered['average_rating']
        filtered = filtered.sort_values('quality_score', ascending=False)
        
        return filtered
    
    def _stratified_sample(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform stratified sampling to maintain category distribution.
        
        Args:
            df: DataFrame to sample from
            
        Returns:
            Sampled DataFrame
        """
        # Calculate samples per category
        category_counts = df['filename'].value_counts()
        samples_per_category = {}
        
        total_categories = len(category_counts)
        base_samples = self.target_size // total_categories
        remaining_samples = self.target_size % total_categories
        
        for category in category_counts.index:
            available = category_counts[category]
            target = min(base_samples, available)
            samples_per_category[category] = target
        
        # Distribute remaining samples to categories with more products
        sorted_categories = category_counts.head(remaining_samples).index
        for category in sorted_categories:
            if samples_per_category[category] < category_counts[category]:
                samples_per_category[category] += 1
        
        # Sample from each category
        sampled_dfs = []
        for category, sample_size in samples_per_category.items():
            category_df = df[df['filename'] == category].head(sample_size)
            sampled_dfs.append(category_df)
            print(f"Sampled {len(category_df)} products from {category}")
        
        return pd.concat(sampled_dfs, ignore_index=True)
    
    def _process_products(self, df: pd.DataFrame) -> List[Dict]:
        """
        Process raw product data into clean format.
        
        Args:
            df: DataFrame to process
            
        Returns:
            List of processed product dictionaries
        """
        processed = []
        
        for _, row in df.iterrows():
            try:
                # Extract and clean data
                product = {
                    'id': row['parent_asin'],
                    'title': str(row['title']).strip(),
                    'description': str(row['description']).strip()[:500],  # Limit description length
                    'category': str(row['main_category']) if pd.notna(row['main_category']) else 'Unknown',
                    'subcategories': row['categories'] if isinstance(row['categories'], list) else [],
                    'store': str(row['store']) if pd.notna(row['store']) else None,
                    'price': float(row['price']) if pd.notna(row['price']) else None,
                    'rating': float(row['average_rating']) if pd.notna(row['average_rating']) else None,
                    'rating_count': int(row['rating_number']) if pd.notna(row['rating_number']) else 0,
                    'features': row['features'] if isinstance(row['features'], list) else [],
                    'image_url': str(row['image']) if pd.notna(row['image']) else None,
                    'filename': row['filename'],
                    'date_available': str(row['date_first_available']) if pd.notna(row['date_first_available']) else None
                }
                
                # Create search text for embeddings
                search_text = f"{product['title']} {product['description']}"
                if product['features']:
                    search_text += " " + " ".join(product['features'][:3])  # Limit features
                
                product['search_text'] = search_text.strip()
                
                processed.append(product)
                
            except Exception as e:
                print(f"Error processing product {row.get('parent_asin', 'unknown')}: {e}")
                continue
        
        return processed
    
    def save_processed_data(self, filepath: str) -> bool:
        """
        Save processed data to JSON file.
        
        Args:
            filepath: Path to save the data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Add metadata
            data_with_metadata = {
                'metadata': {
                    'total_products': len(self.processed_data),
                    'categories': list(set(p['category'] for p in self.processed_data)),
                    'processed_at': datetime.now().isoformat(),
                    'source': 'Amazon Products 2023',
                    'filtering_criteria': 'Priority e-commerce categories with quality filters'
                },
                'products': self.processed_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_with_metadata, f, indent=2, ensure_ascii=False)
            
            print(f"Processed data saved to {filepath}")
            return True
            
        except Exception as e:
            print(f"Error saving processed data: {e}")
            return False
    
    def get_category_distribution(self) -> Dict[str, int]:
        """
        Get distribution of products by category.
        
        Returns:
            Dictionary with category counts
        """
        if not self.processed_data:
            return {}
        
        distribution = {}
        for product in self.processed_data:
            category = product['category']
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution


def main():
    """
    Main function to process and save Amazon data.
    """
    processor = AmazonDataProcessor(target_size=800)
    
    # Load and process data
    products = processor.load_and_filter_data()
    
    if products:
        # Print distribution
        distribution = processor.get_category_distribution()
        print("\nCategory Distribution:")
        for category, count in sorted(distribution.items()):
            print(f"  {category}: {count} products")
        
        # Save processed data
        filepath = "data/processed_products.json"
        success = processor.save_processed_data(filepath)
        
        if success:
            print(f"\n✅ Successfully processed {len(products)} products!")
            print(f"Data saved to: {filepath}")
        else:
            print("❌ Failed to save processed data")
    else:
        print("❌ No products were processed")


if __name__ == "__main__":
    main()