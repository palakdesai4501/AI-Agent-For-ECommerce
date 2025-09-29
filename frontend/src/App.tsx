import React, { useState, useRef } from 'react';
import ChatInterface from './components/ChatInterface';
import ProductGrid from './components/ProductGrid';
import ImageUpload from './components/ImageUpload';
import FloatingImagePanel from './components/FloatingImagePanel';
import AgentInfo from './components/AgentInfo';
import { chatWithAgent, getAgentInfo } from './services/api';
import type { Message, Product, AgentResponse } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [showImagePanel, setShowImagePanel] = useState(false);
  const [agentInfo, setAgentInfo] = useState<any>(null);

  const handleSendMessage = async (message: string, image?: string) => {
    if (!message.trim() && !image) return;

    setLoading(true);

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
      image: image
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      const response: AgentResponse = await chatWithAgent({
        message,
        image
      });

      // Add agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.message,
        timestamp: new Date(),
        products: response.products || [],
        followUp: response.follow_up_questions || []
      };

      setMessages(prev => [...prev, agentMessage]);
      setProducts(response.products || []);

      // Show floating panel for image search results
      if (response.type === 'image_search' && image && response.products && response.products.length > 0) {
        setUploadedImage(image);
        setShowImagePanel(true);
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: 'I encountered an error. Please try again.',
        timestamp: new Date(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleFollowUp = (question: string) => {
    handleSendMessage(question);
  };


  React.useEffect(() => {
    // Load agent info on startup
    getAgentInfo().then(setAgentInfo).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#F2F2F2' }}>
      {/* Header */}
      <header className="glass-card border-b">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: '#000000' }}>
                <span className="font-bold text-sm" style={{ color: '#F2F2F2' }}>C</span>
              </div>
              <div>
                <h1 className="text-lg font-bold" style={{ color: '#000000' }}>Cartly</h1>
                <p className="text-xs" style={{ color: '#B6B09F' }}>AI Shopping Assistant</p>
              </div>
            </div>
            
            {agentInfo && (
              <div className="hidden md:flex items-center px-3 py-1 rounded-md" style={{ backgroundColor: '#EAE4D5' }}>
                <span className="text-xs" style={{ color: '#000000' }}>{agentInfo.total_products} products</span>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        {/* Main Content */}
        <div>
            <div className="glass-card rounded-lg overflow-hidden shadow-lg" style={{ 
              backgroundColor: '#F2F2F2',
              border: '2px solid #B6B09F'
            }}>
              
              {/* Image Upload */}
              <div className="p-4 border-b" style={{ borderColor: '#B6B09F' }}>
                <ImageUpload onImageUpload={(image, message) => handleSendMessage(message, image)} />
              </div>

              {/* Chat Interface with integrated products */}
              <div className="h-[400px] overflow-y-auto">
                <ChatInterface 
                  messages={messages}
                  loading={loading}
                  onFollowUp={handleFollowUp}
                  products={products}
                />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t" style={{ borderColor: '#B6B09F', backgroundColor: '#EAE4D5' }}>
                <MessageInput onSend={handleSendMessage} loading={loading} />
              </div>
            </div>
        </div>
      </div>

      {/* Floating Image Panel */}
      {showImagePanel && (
        <FloatingImagePanel
          image={uploadedImage}
          products={products}
          onClose={() => setShowImagePanel(false)}
        />
      )}
    </div>
  );
}

// Message Input Component
const MessageInput: React.FC<{
  onSend: (message: string) => void;
  loading: boolean;
}> = ({ onSend, loading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !loading) {
      onSend(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-3">
      <div className="flex-1">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask me anything or describe what you're looking for..."
          disabled={loading}
          className="w-full px-4 py-2 text-sm rounded-md focus:outline-none focus:ring-1 disabled:opacity-50"
          style={{ 
            backgroundColor: '#F2F2F2', 
            borderColor: '#B6B09F',
            color: '#000000'
          }}
        />
      </div>
      <button
        type="submit"
        disabled={loading || !message.trim()}
        className="btn-primary px-4 py-2 text-sm rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};

export default App;