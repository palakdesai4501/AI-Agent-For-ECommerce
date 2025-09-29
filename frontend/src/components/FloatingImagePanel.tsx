import React from 'react';
import type { Product } from '../types';

interface FloatingImagePanelProps {
  image: string | null;
  products: Product[];
  onClose: () => void;
}

const FloatingImagePanel: React.FC<FloatingImagePanelProps> = ({ 
  image, 
  products, 
  onClose 
}) => {
  if (!image) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-90vh overflow-hidden">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-900">
            Similar Products Found
          </h3>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-4 overflow-y-auto max-h-80vh">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Uploaded Image */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Your Image</h4>
              <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                <img 
                  src={image} 
                  alt="Uploaded product" 
                  className="w-full h-full object-cover"
                />
              </div>
            </div>

            {/* Similar Products */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">
                Similar Products ({products.length})
              </h4>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {products.slice(0, 6).map((product) => (
                  <div key={product.id} className="flex space-x-3 p-3 bg-gray-50 rounded-lg">
                    <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                      {product.image_url ? (
                        <img 
                          src={product.image_url} 
                          alt={product.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <span className="text-gray-400 text-xs">No image</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h5 className="text-sm font-medium text-gray-900 truncate">
                        {product.title}
                      </h5>
                      <p className="text-xs text-gray-500 mt-1">
                        {product.category}
                      </p>
                      
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center space-x-2">
                          {product.price && (
                            <span className="text-sm font-semibold text-green-600">
                              ${product.price.toFixed(2)}
                            </span>
                          )}
                          {product.rating && (
                            <div className="flex items-center space-x-1">
                              <span className="text-yellow-400 text-xs">★</span>
                              <span className="text-xs text-gray-600">
                                {product.rating.toFixed(1)}
                              </span>
                            </div>
                          )}
                        </div>
                        
                        {product.ai_relevance_score && (
                          <div className="text-xs text-blue-600 font-medium">
                            {product.ai_relevance_score}% match
                          </div>
                        )}
                      </div>

                      {product.ai_recommendation_reason && (
                        <p className="text-xs text-gray-600 mt-2 line-clamp-2">
                          {product.ai_recommendation_reason}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {products.length > 6 && (
            <div className="mt-4 text-center">
              <button
                onClick={onClose}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                View all {products.length} products below
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FloatingImagePanel;