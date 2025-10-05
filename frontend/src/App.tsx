import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import { chatWithAgent, getAgentInfo } from './services/api';
import type { Message, AgentResponse } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [agentInfo, setAgentInfo] = useState<AgentResponse | null>(null);

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

      // Add agent response with products
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.message,
        timestamp: new Date(),
        products: response.products || [],
        followUp: response.follow_up_questions || []
      };

      setMessages(prev => [...prev, agentMessage]);

      // Don't show floating panel - products are displayed in chat

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
    <div className="flex flex-col h-screen" style={{ backgroundColor: '#F2F2F2' }}>
      {/* Header */}
      <header className="glass-card border-b z-50 flex-shrink-0">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            <div className="flex items-center space-x-3">
              <img
                src="/chat.png"
                alt="Cartly"
                className="w-8 h-8 rounded-lg object-cover"
              />
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

      {/* Chat Interface - Scrollable */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <ChatInterface
            messages={messages}
            loading={loading}
            onFollowUp={handleFollowUp}
            products={[]}
          />
        </div>
      </div>

      {/* Message Input - Fixed at bottom */}
      <div className="flex-shrink-0 border-t" style={{ borderColor: '#B6B09F', backgroundColor: '#F2F2F2' }}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <MessageInput onSend={handleSendMessage} loading={loading} uploadedImage={uploadedImage} setUploadedImage={setUploadedImage} />
        </div>
      </div>

    </div>
  );
}

// Message Input Component
const MessageInput: React.FC<{
  onSend: (message: string, image?: string) => void;
  loading: boolean;
  uploadedImage: string | null;
  setUploadedImage: (image: string | null) => void;
}> = ({ onSend, loading, uploadedImage, setUploadedImage }) => {
  const [message, setMessage] = useState('');
  const [showUploadMenu, setShowUploadMenu] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((message.trim() || uploadedImage) && !loading) {
      onSend(message || "Find products similar to this image", uploadedImage || undefined);
      setMessage('');
      setUploadedImage(null);
    }
  };

  const handleFile = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageData = e.target?.result as string;
        setUploadedImage(imageData);
        setShowUploadMenu(false);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <>
      {/* Drag overlay */}
      {dragActive && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div
            className="border-4 border-dashed rounded-lg p-12"
            style={{ borderColor: '#B6B09F', backgroundColor: '#F2F2F2' }}
          >
            <div className="text-center">
              <svg className="w-16 h-16 mx-auto mb-4" style={{ color: '#B6B09F' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="text-lg font-semibold" style={{ color: '#000000' }}>Drop image here</p>
              <p className="text-sm" style={{ color: '#B6B09F' }}>PNG or JPG up to 10MB</p>
            </div>
          </div>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        className="space-y-2"
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {/* Image thumbnail preview */}
        {uploadedImage && (
          <div className="flex items-center space-x-3 p-3 rounded-xl" style={{ backgroundColor: '#FFFFFF', border: '1px solid #B6B09F', boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)' }}>
            <img
              src={uploadedImage}
              alt="Upload preview"
              className="w-14 h-14 object-cover rounded-lg"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate" style={{ color: '#000000' }}>Image attached</p>
              <p className="text-xs" style={{ color: '#B6B09F' }}>Ready to send</p>
            </div>
            <button
              type="button"
              onClick={() => setUploadedImage(null)}
              className="p-1.5 rounded-lg hover:bg-opacity-80 transition-colors"
              style={{ backgroundColor: '#EAE4D5', color: '#000000' }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Input bar */}
        <div className="flex space-x-2">
          {/* Plus button with upload menu */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowUploadMenu(!showUploadMenu)}
              className="p-2.5 rounded-lg transition-all hover:bg-opacity-80"
              style={{ backgroundColor: '#EAE4D5', color: '#000000' }}
              disabled={loading}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>

            {/* Upload menu dropdown */}
            {showUploadMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowUploadMenu(false)}
                />
                <div
                  className="absolute bottom-full left-0 mb-2 rounded-xl shadow-xl z-20 overflow-hidden"
                  style={{ backgroundColor: '#F2F2F2', border: '1px solid #B6B09F', minWidth: '200px' }}
                >
                  <button
                    type="button"
                    onClick={() => {
                      fileInputRef.current?.click();
                      setShowUploadMenu(false);
                    }}
                    className="w-full flex items-center space-x-3 px-4 py-3 text-left text-sm transition-colors"
                    style={{ color: '#000000' }}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#EAE4D5'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                  >
                    <svg className="w-5 h-5" style={{ color: '#B6B09F' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="font-medium">Upload Image</span>
                  </button>
                </div>
              </>
            )}

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg"
              onChange={handleFileInput}
              className="hidden"
            />
          </div>

          {/* Message input */}
          <div className="flex-1">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask me anything or describe what you're looking for..."
              disabled={loading}
              className="w-full px-5 py-3 text-sm rounded-xl focus:outline-none focus:ring-2 disabled:opacity-50 transition-all"
              style={{
                backgroundColor: '#FFFFFF',
                border: '1px solid #B6B09F',
                color: '#000000',
                boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)'
              }}
            />
          </div>

          {/* Send button */}
          <button
            type="submit"
            disabled={loading || (!message.trim() && !uploadedImage)}
            className="btn-primary px-6 py-3 text-sm rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105"
          >
            {loading ? (
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              'Send'
            )}
          </button>
        </div>
      </form>
    </>
  );
};

export default App;