# Cartly - AI-Powered E-commerce Shopping Assistant

Cartly is an intelligent shopping assistant that helps users find products through natural conversation and image-based search. The system combines advanced AI capabilities with a modern, responsive web interface to provide personalized product recommendations.

## 🚀 Features

- **Natural Language Processing**: Chat with the AI assistant using natural language queries
- **Image-Based Search**: Upload images or provide image URLs to find similar products
- **Real-time Product Recommendations**: Get instant, relevant product suggestions
- **Modern UI/UX**: Clean, responsive interface with floating product cards
- **Vector Search**: Advanced similarity search using Pinecone vector database
- **AI Reranking**: Intelligent product ranking based on user intent

## 🏗️ Technology Stack

### Frontend
- **React 18** with TypeScript for type-safe, component-based UI development
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for utility-first styling and responsive design
- **Custom CSS Components** for enhanced visual appeal

**Why React + TypeScript?**
- Type safety prevents runtime errors and improves developer experience
- Component reusability and maintainability
- Excellent ecosystem and community support
- Vite provides faster development builds compared to Create React App

### Backend
- **Python 3.8+** for robust backend services
- **Flask** for lightweight, flexible API server
- **BAML (BoundaryML)** for LLM function definitions and management
- **Google Gemini API** for AI-powered text and image analysis
- **Pinecone** for vector similarity search
- **Pandas** for data processing and manipulation

**Why this backend stack?**
- Python's excellent AI/ML ecosystem
- Flask provides simplicity and flexibility for API development
- BAML offers better LLM management than direct API calls
- Pinecone provides scalable vector search capabilities
- Gemini API offers competitive pricing and good performance

### AI & Search
- **Google Gemini 2.0 Flash Lite** for conversational AI
- **Vector Embeddings** for semantic product search
- **AI Reranking** for intelligent result ordering
- **Image Analysis** for visual product matching

## 📁 Project Structure

```
AIAgent-comerceWebsite/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API service layer
│   │   └── types.tsx        # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
├── backend/                 # Python backend services
│   ├── src/
│   │   ├── conversational_agent.py  # Main AI agent logic
│   │   ├── search_engine.py         # Product search functionality
│   │   ├── data_processor.py        # Data processing utilities
│   │   └── vector_store.py          # Vector database operations
│   ├── baml_src/            # BAML function definitions
│   ├── api_server.py        # Flask API server
│   └── requirements.txt
├── data/                    # Product data and assets
│   └── processed_products.json
├── .gitignore
└── README.md
```

## 🛠️ Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Pinecone account and API key
- Google Cloud account with Gemini API access

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   ```
   Edit `.env` with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_ENVIRONMENT=your_pinecone_environment
   ```

5. **Generate processed product data:**
   ```bash
   python src/data_processor.py
   ```
   This will create `data/processed_products.json` with 800 curated products.

6. **Start the backend server:**
   ```bash
   python api_server.py
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5173`

## 🔧 API Documentation

### Endpoints

#### `POST /api/chat`
Send a message to the AI agent.

**Request Body:**
```json
{
  "message": "Find me wireless headphones under $100",
  "image": "base64_encoded_image_or_url" // optional
}
```

**Response:**
```json
{
  "response": "I found some great wireless headphones under $100...",
  "products": [
    {
      "id": "product_123",
      "title": "Wireless Headphones",
      "price": 89.99,
      "category": "Electronics",
      "rating": 4.5,
      "image_url": "https://example.com/image.jpg",
      "ai_relevance_score": 95
    }
  ],
  "followUp": ["Show me more options", "What about noise cancellation?"]
}
```

#### `GET /api/agent-info`
Get information about the AI agent.

**Response:**
```json
{
  "name": "Cartly",
  "total_products": 1250,
  "capabilities": [
    "Product recommendations",
    "Image-based search",
    "Price comparisons",
    "Category filtering"
  ],
  "available_categories": ["Electronics", "Clothing", "Home & Kitchen"]
}
```

## 🎨 UI/UX Design Decisions

### Color Palette
- **Primary**: `#F2F2F2` (Light Gray) - Clean, professional background
- **Secondary**: `#EAE4D5` (Light Beige) - Warm accent color
- **Accent**: `#B6B09F` (Medium Taupe) - Subtle borders and text
- **Text**: `#000000` (Black) - High contrast for readability

### Design Principles
- **Minimalistic**: Clean, uncluttered interface focusing on functionality
- **Floating Cards**: Product cards with subtle shadows and hover effects
- **Responsive**: Mobile-first design that works on all screen sizes
- **Accessible**: High contrast ratios and clear typography
- **Professional**: No emojis, using clean SVG icons instead

## 🚀 Deployment

### Frontend (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy dist/ folder to your hosting service
```

### Backend (Railway/Heroku)
```bash
cd backend
# Add Procfile with: web: python api_server.py
# Deploy with your preferred platform
```

## 📊 Performance Optimizations

- **Lazy Loading**: Components load only when needed
- **Image Optimization**: Compressed product images
- **Vector Search**: Efficient similarity search with Pinecone
- **Caching**: API responses cached for better performance
- **Code Splitting**: Frontend code split for faster initial load

## 🔒 Security Considerations

- API keys stored in environment variables
- CORS properly configured for frontend-backend communication
- Input validation on all API endpoints
- Rate limiting implemented for API calls

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Pinecone for vector search infrastructure
- React and Vite communities for excellent tooling
- Tailwind CSS for utility-first styling approach

## 📞 Support

For support, email support@cartly.com or create an issue in this repository.

---

**Note**: This project includes a `streamlit_app.py` file as a backup/alternative implementation, which is excluded from the main deployment via `.gitignore` but kept for reference purposes.
# AI-Agent-For-ECommerce
