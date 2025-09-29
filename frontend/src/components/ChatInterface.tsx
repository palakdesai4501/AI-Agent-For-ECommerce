import React from 'react';
import type { Message, Product } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  loading: boolean;
  onFollowUp: (question: string) => void;
  products?: Product[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ messages, loading, onFollowUp, products = [] }) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

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
    <div className="p-4 space-y-4">
      {messages.map((message) => (
        <MessageBubble 
          key={message.id} 
          message={message} 
          onFollowUp={onFollowUp}
        />
      ))}
      
      {/* Product Cards */}
      {products.length > 0 && (
        <div className="mt-4">
        <div className="flex items-center mb-3">
          <h3 className="text-sm font-semibold" style={{ color: '#000000' }}>Found Products</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {products.slice(0, 5).map((product) => (
            <FloatingProductCard key={product.id} product={product} />
          ))}
        </div>
        </div>
      )}
      
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

          {/* Products count */}
          {message.products && message.products.length > 0 && (
            <div className="mt-2 px-2 py-1 rounded text-xs inline-block" style={{ backgroundColor: '#EAE4D5' }}>
              <span style={{ color: '#000000' }}>Found {message.products.length} products</span>
            </div>
          )}

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

const FloatingProductCard: React.FC<{ product: Product }> = ({ product }) => {
  return (
    <div className="floating-card glass-card rounded-lg p-3 transition-all duration-200 shadow-lg hover:shadow-xl" style={{ 
      borderColor: '#B6B09F',
      backgroundColor: '#F2F2F2',
      transform: 'translateY(-2px)'
    }}>
      <div className="flex flex-col h-full">
        {/* Product Image - Full size floating tile */}
        <div className="relative mb-3">
          {product.image_url ? (
            <div className="w-full h-32 rounded-lg overflow-hidden shadow-md">
              <img 
                src={product.image_url} 
                alt={product.title}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
              />
            </div>
          ) : (
            <div className="w-full h-32 rounded-lg flex items-center justify-center shadow-md" style={{ backgroundColor: '#EAE4D5' }}>
              <svg className="w-8 h-8" style={{ color: '#B6B09F' }} fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
          )}
          {product.rating && (
            <div className="absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium shadow-md" style={{ backgroundColor: '#F2F2F2' }}>
              <span style={{ color: '#000000' }}>{product.rating}★</span>
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="flex-1">
          <h3 className="font-semibold text-sm mb-2 line-clamp-2" style={{ color: '#000000' }}>
            {product.title}
          </h3>
          
          <div className="space-y-1 mb-3">
            <div className="text-xs font-medium" style={{ color: '#B6B09F' }}>
              {product.category}
            </div>
            {product.price && (
              <div className="text-lg font-bold" style={{ color: '#000000' }}>
                ${product.price}
              </div>
            )}
          </div>

          {/* AI Score if available */}
          {product.ai_relevance_score && (
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium" style={{ color: '#B6B09F' }}>AI Score</span>
              <div className="flex items-center space-x-2">
                <div className="w-16 h-2 rounded-full overflow-hidden" style={{ backgroundColor: '#EAE4D5' }}>
                  <div 
                    className="h-full rounded-full transition-all duration-300"
                    style={{ 
                      width: `${product.ai_relevance_score}%`,
                      backgroundColor: '#B6B09F'
                    }}
                  ></div>
                </div>
                <span className="text-xs font-bold" style={{ color: '#000000' }}>{product.ai_relevance_score}%</span>
              </div>
            </div>
          )}

          {/* Action Button */}
          <button className="w-full py-2 btn-primary text-sm rounded-md font-medium hover:scale-105 transition-transform duration-200">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;