import React from 'react';
import type { Product } from '../types';

interface ProductGridProps {
  products: Product[];
}

const ProductGrid: React.FC<ProductGridProps> = ({ products }) => {
  if (products.length === 0) return null;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">
        Products ({products.length})
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      
      {/* Product Image */}
      <div className="aspect-square bg-gray-100 overflow-hidden">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        <h3 className="font-medium text-gray-900 text-sm line-clamp-2 mb-2">
          {product.title}
        </h3>
        
        <p className="text-xs text-gray-500 mb-3">{product.category}</p>

        {/* Rating and Price */}
        <div className="flex items-center justify-between mb-3">
          {product.rating && (
            <div className="flex items-center space-x-1">
              <div className="flex text-yellow-400">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className={`text-xs ${i < Math.floor(product.rating!) ? 'text-yellow-400' : 'text-gray-300'}`}>
                    ★
                  </span>
                ))}
              </div>
              <span className="text-xs text-gray-600">
                {product.rating.toFixed(1)} ({product.rating_count})
              </span>
            </div>
          )}
          
          {product.price && (
            <span className="text-lg font-semibold text-green-600">
              ${product.price.toFixed(2)}
            </span>
          )}
        </div>

        {/* AI Scores */}
        {(product.ai_relevance_score || product.similarity_score) && (
          <div className="flex space-x-2 mb-3">
            {product.ai_relevance_score && (
              <div className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                AI: {product.ai_relevance_score}/100
              </div>
            )}
            {product.similarity_score && (
              <div className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                Match: {(product.similarity_score * 100).toFixed(0)}%
              </div>
            )}
          </div>
        )}

        {/* AI Recommendation */}
        {product.ai_recommendation_reason && (
          <div className="mt-3 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-800 font-medium mb-1">Why this product:</p>
            <p className="text-xs text-blue-700 line-clamp-3">
              {product.ai_recommendation_reason}
            </p>
          </div>
        )}

        {/* Description */}
        {product.description && (
          <p className="text-xs text-gray-600 mt-3 line-clamp-2">
            {product.description}
          </p>
        )}
      </div>
    </div>
  );
};

export default ProductGrid;