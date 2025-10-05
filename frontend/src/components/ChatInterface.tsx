import React from 'react';
import type { Message, Product } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  loading: boolean;
  onFollowUp: (question: string) => void;
  products?: Product[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, loading, onFollowUp }) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const [selectedProduct, setSelectedProduct] = React.useState<Product | null>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0 && !loading) {
    return (
      <div className="p-6 text-center">
        <div className="w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4" style={{ backgroundColor: '#EAE4D5' }}>
          <img src="/chat.png" alt="Chat" className="w-6 h-6 object-contain" />
        </div>
        <h3 className="text-lg font-semibold mb-2" style={{ color: '#000000' }}>Hi! I'm Cartly</h3>
        <p className="text-sm mb-4" style={{ color: '#B6B09F' }}>Your AI shopping assistant. I can help you with:</p>
        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-center space-x-2 rounded-md px-3 py-2" style={{ backgroundColor: '#EAE4D5' }}>
            <svg className="w-4 h-4" style={{ color: '#B6B09F' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h4l4 4 4-4h4c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
            </svg>
            <span className="font-medium" style={{ color: '#000000' }}>General conversation</span>
          </div>
          <div className="flex items-center justify-center space-x-2 rounded-md px-3 py-2" style={{ backgroundColor: '#EAE4D5' }}>
            <svg className="w-4 h-4" style={{ color: '#B6B09F' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <span className="font-medium" style={{ color: '#000000' }}>Product recommendations</span>
          </div>
          <div className="flex items-center justify-center space-x-2 rounded-md px-3 py-2" style={{ backgroundColor: '#EAE4D5' }}>
            <svg className="w-4 h-4" style={{ color: '#B6B09F' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
            </svg>
            <span className="font-medium" style={{ color: '#000000' }}>Image-based search</span>
          </div>
        </div>
        <div className="mt-4 space-x-2">
          <button
            onClick={() => onFollowUp("What's your name?")}
            className="btn-primary px-3 py-1 text-xs rounded-md"
          >
            What's your name?
          </button>
          <button
            onClick={() => onFollowUp("Find me wireless headphones")}
            className="btn-secondary px-3 py-1 text-xs rounded-md"
          >
            Find products
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="py-6 space-y-6">
      {messages.map((message, index) => (
        <div key={message.id}>
          <MessageBubble
            message={message}
            onFollowUp={onFollowUp}
          />

          {/* Show products for this specific message */}
          {message.products && message.products.length > 0 && (
            <div className="mt-6">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {message.products.map((product) => (
                  <ProductCard key={product.id} product={product} onView={() => setSelectedProduct(product)} />
                ))}
              </div>
            </div>
          )}

          {/* Add separator between different search queries */}
          {index < messages.length - 1 && (
            <div className="mt-8 mb-2">
              <div className="h-px" style={{ backgroundColor: '#EAE4D5' }} />
            </div>
          )}
        </div>
      ))}

      {loading && (
        <div className="flex items-center space-x-2" style={{ color: '#B6B09F' }}>
          <div className="w-6 h-6 rounded-md flex items-center justify-center" style={{ backgroundColor: '#000000' }}>
            <svg className="w-3 h-3 animate-pulse" style={{ color: '#F2F2F2' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 18c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12L8.1 13h7.45c.75 0 1.41-.41 1.75-1.03L21.7 4H5.21l-.94-2H1zm16 16c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </div>
          <span className="text-xs">Cartly is thinking...</span>
        </div>
      )}

      <div ref={messagesEndRef} />

      {/* Product Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedProduct(null)} />

          {/* Modal */}
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl" style={{ backgroundColor: '#FFFFFF', border: '1px solid #B6B09F', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)' }}>
            {/* Close button - top right */}
            <button
              onClick={() => setSelectedProduct(null)}
              className="absolute right-6 top-6 z-10 p-2 rounded-lg transition-colors hover:bg-opacity-80"
              style={{ backgroundColor: '#EAE4D5', color: '#000000' }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Content */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
              {/* Left: Image */}
              <div className="flex items-center justify-center" style={{ backgroundColor: '#F2F2F2', borderRadius: '12px', padding: '24px' }}>
                <div className="w-full max-w-md">
                  {selectedProduct.image_url ? (
                    <img
                      src={selectedProduct.image_url}
                      alt={selectedProduct.title}
                      className="w-full h-auto object-contain rounded-lg"
                      style={{ maxHeight: '400px' }}
                    />
                  ) : (
                    <div className="w-full h-64 flex items-center justify-center" style={{ color: '#B6B09F' }}>
                      <div className="text-center">
                        <svg className="w-16 h-16 mx-auto mb-2" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                        </svg>
                        <span className="text-sm">No image available</span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Right: Details */}
              <div className="flex flex-col">
                {/* Title */}
                <h2 className="text-2xl font-bold mb-3" style={{ color: '#000000', lineHeight: '1.3' }}>
                  {selectedProduct.title}
                </h2>

                {/* Category */}
                <div className="text-sm font-medium mb-4 px-3 py-1.5 rounded-lg inline-block w-fit" style={{ backgroundColor: '#EAE4D5', color: '#000000' }}>
                  {selectedProduct.category}
                </div>

                {/* Rating */}
                {selectedProduct.rating && (
                  <div className="flex items-center gap-2 mb-4">
                    <div className="flex items-center gap-1">
                      <svg className="w-5 h-5" style={{ color: '#FFD700' }} fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      <span className="text-lg font-semibold" style={{ color: '#000000' }}>{selectedProduct.rating}</span>
                    </div>
                    {selectedProduct.rating_count && (
                      <span className="text-sm" style={{ color: '#B6B09F' }}>({selectedProduct.rating_count.toLocaleString()} reviews)</span>
                    )}
                  </div>
                )}

                {/* Price */}
                {selectedProduct.price && (
                  <div className="text-4xl font-bold mb-6" style={{ color: '#000000' }}>
                    ${selectedProduct.price}
                  </div>
                )}

                {/* Description */}
                {selectedProduct.description && (
                  <div className="mb-6">
                    <h3 className="text-sm font-semibold mb-2" style={{ color: '#000000' }}>Description</h3>
                    <p className="text-base leading-relaxed" style={{ color: '#000000', lineHeight: '1.6' }}>
                      {selectedProduct.description}
                    </p>
                  </div>
                )}

                {/* Spacer */}
                <div className="flex-1" />

                {/* Buttons */}
                <div className="flex gap-3 mt-6 pt-6 border-t" style={{ borderColor: '#EAE4D5' }}>
                  <a
                    href={selectedProduct.product_url || selectedProduct.image_url || '#'}
                    target="_blank"
                    rel="noreferrer"
                    className="flex-1 btn-primary px-6 py-3 text-sm font-semibold rounded-xl text-center transition-all hover:scale-102"
                  >
                    Open Link
                  </a>
                  <button
                    onClick={() => setSelectedProduct(null)}
                    className="px-6 py-3 text-sm font-semibold rounded-xl transition-all"
                    style={{ backgroundColor: '#EAE4D5', color: '#000000' }}
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const MessageBubble: React.FC<{
  message: Message;
  onFollowUp: (question: string) => void;
}> = ({ message, onFollowUp }) => {
  const isUser = message.type === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-lg ${isUser ? 'flex-row-reverse' : 'flex-row'} space-x-2`}>
        
        {/* Avatar */}
        <div className={`w-6 h-6 rounded-md flex items-center justify-center flex-shrink-0 ${
          isUser ? 'ml-2' : 'mr-2'
        }`} style={{ 
          backgroundColor: isUser ? '#000000' : '#EAE4D5' 
        }}>
          {isUser ? (
            <svg className="w-3 h-3" style={{ color: '#F2F2F2' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
            </svg>
          ) : (
            <svg className="w-3 h-3" style={{ color: '#000000' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M7 18c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zM1 2v2h2l3.6 7.59-1.35 2.45c-.16.28-.25.61-.25.96 0 1.1.9 2 2 2h12v-2H7.42c-.14 0-.25-.11-.25-.25l.03-.12L8.1 13h7.45c.75 0 1.41-.41 1.75-1.03L21.7 4H5.21l-.94-2H1zm16 16c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          )}
        </div>

        {/* Message Content */}
        <div className={`rounded-lg px-3 py-2 ${
          isUser 
            ? 'chat-bubble-user' 
            : message.error 
              ? 'bg-red-50 text-red-800 border border-red-200'
              : 'chat-bubble-agent'
        }`}>
          
          {/* Image if present */}
          {message.image && (
            <div className="mb-2">
              <img 
                src={message.image} 
                alt="Uploaded" 
                className="max-w-32 max-h-24 object-cover rounded-md"
              />
            </div>
          )}

          {/* Message text */}
          <p className="text-xs whitespace-pre-wrap leading-relaxed">{message.content}</p>

          {/* Follow-up suggestions */}
          {message.followUp && message.followUp.length > 0 && (
            <div className="mt-2 space-y-1">
              <p className="text-xs font-medium" style={{ color: '#B6B09F' }}>Suggestions:</p>
              <div className="space-y-1">
                {message.followUp.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => onFollowUp(suggestion)}
                    className="block w-full text-left px-2 py-1 text-xs rounded transition-colors"
                    style={{ 
                      backgroundColor: '#EAE4D5',
                      color: '#000000'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#B6B09F';
                      e.currentTarget.style.color = '#F2F2F2';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#EAE4D5';
                      e.currentTarget.style.color = '#000000';
                    }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const ProductCard: React.FC<{ product: Product, onView: () => void }> = ({ product, onView }) => {
  return (
    <div className="glass-card rounded-xl overflow-hidden transition-all duration-200 hover:shadow-xl flex flex-col h-full" style={{
      border: '1px solid #B6B09F',
      backgroundColor: '#FFFFFF'
    }}>
      {/* Product Image */}
      <div className="relative w-full aspect-square overflow-hidden" style={{ backgroundColor: '#F2F2F2' }}>
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.title}
            className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center" style={{ backgroundColor: '#EAE4D5' }}>
            <svg className="w-12 h-12" style={{ color: '#B6B09F' }} fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
            </svg>
          </div>
        )}
        {/* Rating badge - top right corner */}
        {product.rating && (
          <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full text-xs font-semibold shadow-lg" style={{ backgroundColor: '#FFFFFF', color: '#000000' }}>
            {product.rating}★
          </div>
        )}
      </div>

      {/* Product Info - with padding */}
      <div className="p-4 flex flex-col flex-1">
        {/* Title */}
        <h3 className="font-semibold text-sm mb-2 line-clamp-2 min-h-[40px]" style={{ color: '#000000' }}>
          {product.title}
        </h3>

        {/* Category */}
        <div className="text-xs mb-2" style={{ color: '#B6B09F' }}>
          {product.category}
        </div>

        {/* Price */}
        {product.price && (
          <div className="text-xl font-bold mb-3" style={{ color: '#000000' }}>
            ${product.price}
          </div>
        )}

        {/* AI Score if available */}
        {product.ai_relevance_score && (
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-medium" style={{ color: '#B6B09F' }}>Match</span>
            <div className="flex items-center space-x-2">
              <div className="w-16 h-2 rounded-full overflow-hidden" style={{ backgroundColor: '#EAE4D5' }}>
                <div
                  className="h-full rounded-full transition-all duration-300"
                  style={{
                    width: `${product.ai_relevance_score}%`,
                    backgroundColor: '#000000'
                  }}
                ></div>
              </div>
              <span className="text-xs font-semibold" style={{ color: '#000000' }}>{product.ai_relevance_score}%</span>
            </div>
          </div>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Action Button - anchored to bottom */}
        <button onClick={onView} className="w-full py-2.5 btn-primary text-sm rounded-lg font-medium transition-all hover:scale-102">
          View Details
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;