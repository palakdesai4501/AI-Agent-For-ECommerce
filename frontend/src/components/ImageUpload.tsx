import React, { useState, useRef } from 'react';

interface ImageUploadProps {
  onImageUpload: (imageData: string, message: string) => void;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onImageUpload }) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState('');
  const [activeTab, setActiveTab] = useState<'upload' | 'url'>('upload');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageData = e.target?.result as string;
        setUploadedImage(imageData);
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

  const handleSearch = () => {
    if (uploadedImage) {
      onImageUpload(uploadedImage, "Find products similar to this image");
      setUploadedImage(null);
    }
  };

  const handleUrlSearch = () => {
    if (imageUrl.trim()) {
      onImageUpload(imageUrl, "Find products similar to this image");
      setImageUrl('');
    }
  };

  const removeImage = () => {
    setUploadedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-semibold" style={{ color: '#000000' }}>Image Search</span>
        </div>
        <span className="text-xs" style={{ color: '#B6B09F' }}>Upload photo or URL</span>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 rounded-md p-1" style={{ backgroundColor: '#EAE4D5' }}>
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex-1 py-2 px-3 rounded text-xs font-medium transition-colors ${
            activeTab === 'upload'
              ? 'shadow-sm'
              : ''
          }`}
          style={{
            backgroundColor: activeTab === 'upload' ? '#F2F2F2' : 'transparent',
            color: '#000000'
          }}
        >
          Upload
        </button>
        <button
          onClick={() => setActiveTab('url')}
          className={`flex-1 py-2 px-3 rounded text-xs font-medium transition-colors ${
            activeTab === 'url'
              ? 'shadow-sm'
              : ''
          }`}
          style={{
            backgroundColor: activeTab === 'url' ? '#F2F2F2' : 'transparent',
            color: '#000000'
          }}
        >
          URL
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div>
          {!uploadedImage ? (
            <div
              className={`relative border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                dragActive ? 'opacity-80' : ''
              }`}
              style={{
                borderColor: dragActive ? '#B6B09F' : '#B6B09F',
                backgroundColor: dragActive ? '#EAE4D5' : '#F2F2F2'
              }}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileInput}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              
              <div className="space-y-2">
                <div className="w-8 h-8 mx-auto rounded-md flex items-center justify-center" style={{ backgroundColor: '#EAE4D5' }}>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" style={{ color: '#B6B09F' }}>
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="text-sm font-medium" style={{ color: '#000000' }}>
                  <span style={{ color: '#B6B09F' }}>Click to upload</span> or drag and drop
                </div>
                <div className="text-xs" style={{ color: '#B6B09F' }}>PNG, JPG up to 10MB</div>
              </div>
            </div>
          ) : (
            <div className="relative">
              <div className="flex items-center space-x-3 p-3 rounded-lg" style={{ backgroundColor: '#EAE4D5', borderColor: '#B6B09F' }}>
                <img
                  src={uploadedImage}
                  alt="Uploaded"
                  className="w-12 h-12 object-cover rounded-md"
                />
                <div className="flex-1">
                  <p className="text-sm font-semibold" style={{ color: '#000000' }}>Image ready</p>
                  <p className="text-xs" style={{ color: '#B6B09F' }}>Click "Find Similar" to search</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={handleSearch}
                    className="btn-primary px-3 py-1 text-xs rounded-md"
                  >
                    Find Similar
                  </button>
                  <button
                    onClick={removeImage}
                    className="p-1 transition-colors"
                    style={{ color: '#B6B09F' }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#000000'}
                    onMouseLeave={(e) => e.currentTarget.style.color = '#B6B09F'}
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* URL Tab */}
      {activeTab === 'url' && (
        <div className="space-y-2">
          <div className="flex space-x-2">
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
              className="flex-1 px-3 py-2 text-sm rounded-md focus:outline-none focus:ring-1"
              style={{ 
                backgroundColor: '#F2F2F2', 
                borderColor: '#B6B09F',
                color: '#000000'
              }}
            />
            <button
              onClick={handleUrlSearch}
              disabled={!imageUrl.trim()}
              className="btn-primary px-3 py-2 text-xs rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Search
            </button>
          </div>
          <p className="text-xs" style={{ color: '#B6B09F' }}>
            Enter a direct image URL
          </p>
        </div>
      )}
    </div>
  );
};

export default ImageUpload;