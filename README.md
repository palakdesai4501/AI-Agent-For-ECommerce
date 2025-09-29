# 🛒 Cartly - AI-Powered E-commerce Shopping Assistant

> An intelligent shopping assistant that combines natural language processing, computer vision, and vector search to help users find products through conversation and image uploads.

![Made with React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Made with Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python)
![Powered by Gemini](https://img.shields.io/badge/Gemini-API-4285F4?logo=google)
![Vector DB](https://img.shields.io/badge/Pinecone-Vector%20DB-00D4AA)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)

---

## Overview

**Cartly** is a modern e-commerce AI agent that provides personalized product recommendations through:
- **Natural language conversations** (text queries)
- **Image-based search** (visual product matching)
- **Semantic understanding** of user intent

The system uses vector embeddings and AI-powered reranking to deliver highly relevant product suggestions from a curated catalog of 800 products across 20+ categories.

---

## ✨ Key Features

### 🗣️ Natural Conversation
- Chat naturally with the AI assistant
- Understands context and user intent
- Provides conversational product recommendations
- Offers follow-up suggestions

### 🖼️ Image Search
- Upload product images (PNG/JPG)
- AI analyzes visual attributes (color, style, category)
- Finds similar products in catalog
- Drag-and-drop support

### 🎯 Smart Product Matching
- **Vector similarity search** with Pinecone
- **Minimum similarity threshold** (35%) filters irrelevant results
- **Multiple view indexing** per product (features, descriptions, categories)
- Real-time search with sub-second response times

### 💬 Clean Chat Interface
- ChatGPT-like conversational UI
- Products displayed with images below each response
- Persistent conversation history
- Mobile-responsive design

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (React + TypeScript + Vite)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND API SERVER                        │
│                         (Flask/Python)                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Conversational Agent                          │ │
│  │  - Intent Classification (BAML)                            │ │
│  │  - Query Refinement                                        │ │
│  │  - Response Generation                                     │ │
│  └────────────┬────────────────────────────┬──────────────────┘ │
│               │                            │                    │
│               ▼                            ▼                    │
│  ┌─────────────────────┐    ┌──────────────────────────────┐  │
│  │   Search Engine     │    │    Image Analysis            │  │
│  │  - Vector Search    │    │  - Gemini Vision             │  │
│  │  - Filtering        │    │  - Attribute Extraction      │  │
│  │  - Ranking          │    │  - Query Generation (BAML)   │  │
│  └──────────┬──────────┘    └──────────────┬───────────────┘  │
└─────────────┼──────────────────────────────┼───────────────────┘
              │                              │
              ▼                              ▼
┌──────────────────────────┐    ┌─────────────────────────────┐
│   Pinecone Vector Store  │    │    Gemini 2.0 Flash Lite    │
│  - 800 products          │    │  - Vision Analysis          │
│  - 384-dim embeddings    │    │  - Intent Classification    │
│  - Cosine similarity     │    │  - Query Refinement         │
└──────────────────────────┘    └─────────────────────────────┘
```

### Component Flow

#### 1️⃣ **Text Search Flow**

```
User Query → HandleUserQuery (BAML) → Intent: PRODUCT_RECOMMENDATION
           ↓
    Refined Query → Vector Store Search (Pinecone)
           ↓
    Filter by similarity > 0.35 → Return top 3 products
           ↓
    Display in Chat Interface
```

#### 2️⃣ **Image Search Flow**

```
Image Upload → Gemini Vision API → Structured Attributes
            ↓
     AnalyzeProductImage (BAML) → Focused Search Query
            ↓
     Vector Store Search (Pinecone) → Filter by similarity > 0.35
            ↓
     Return top 3 matching products → Display in Chat
```

#### 3️⃣ **General Conversation Flow**

```
User Query → HandleUserQuery (BAML) → Intent: GENERAL_CONVERSATION
           ↓
    Direct Reply (no product search)
           ↓
    Display in Chat with Follow-up Suggestions
```

---

## 🛠️ Technology Stack

### Frontend
| Technology | Purpose | Why? |
|------------|---------|------|
| **React 18** | UI Framework | Component-based architecture, rich ecosystem |
| **TypeScript** | Type Safety | Prevents runtime errors, better IDE support |
| **Vite** | Build Tool | 10x faster than CRA, optimized builds |
| **Tailwind CSS** | Styling | Utility-first, responsive, maintainable |

### Backend
| Technology | Purpose | Why? |
|------------|---------|------|
| **Python 3.8+** | Runtime | Best AI/ML ecosystem |
| **Flask** | API Server | Lightweight, flexible, easy to deploy |
| **BAML** | LLM Management | Type-safe LLM functions, better than raw API calls |
| **Pinecone** | Vector DB | Scalable, fast similarity search |
| **Sentence Transformers** | Embeddings | State-of-the-art semantic embeddings |

### AI Services
| Service | Purpose | Model |
|---------|---------|-------|
| **Google Gemini** | Vision + Text | `gemini-2.0-flash-lite` |
| **all-MiniLM-L6-v2** | Embeddings | 384-dim vectors, fast inference |

---

## 📁 Project Structure

```
AIAgent-comerceWebsite/
│
├── frontend/                          # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx      # Main chat UI with message bubbles
│   │   │   ├── ProductCard.tsx        # Individual product display
│   │   │   └── FloatingImagePanel.tsx # (Deprecated) Image preview panel
│   │   ├── services/
│   │   │   └── api.ts                 # API client for backend
│   │   ├── types.tsx                  # TypeScript type definitions
│   │   ├── App.tsx                    # Main app component
│   │   └── index.css                  # Global styles + Tailwind
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                           # Python backend
│   ├── src/
│   │   ├── conversational_agent.py    # 🧠 Main AI agent logic
│   │   │   ├── process_message()      # Entry point for all queries
│   │   │   ├── _handle_product_search()
│   │   │   ├── _handle_image_search()
│   │   │   └── _analyze_image_content()
│   │   │
│   │   ├── search_engine.py           # 🔍 Product search engine
│   │   │   ├── search()               # Main search function
│   │   │   └── Vector store integration
│   │   │
│   │   ├── vector_store.py            # 📊 Pinecone vector operations
│   │   │   ├── upsert_products()      # Index products
│   │   │   ├── search_similar_products() # Similarity search
│   │   │   └── _build_views_for_product() # Multi-view indexing
│   │   │
│   │   └── data_processor.py          # 📦 Data processing utilities
│   │       └── Process raw Amazon data
│   │
│   ├── baml_src/                      # BAML function definitions
│   │   └── ecommerce.baml
│   │       ├── HandleUserQuery        # Intent classification
│   │       ├── AnalyzeProductImage    # Image → search query
│   │       └── HandleGeneralConversation
│   │
│   ├── baml_client/                   # Auto-generated BAML client
│   ├── api_server.py                  # Flask API server
│   ├── requirements.txt               # Python dependencies
│   └── .env                           # Environment variables
│
├── data/
│   └── processed_products.json        # 800 curated products
│
└── README.md
```

---

## 🔄 How It Works

### 1. User Sends Query (Text or Image)

```javascript
// Frontend sends request
await chatWithAgent({
  message: "Find me running shoes",
  image: base64Image // optional
})
```

### 2. Backend Processes Intent

```python
# conversational_agent.py
directive = b.HandleUserQuery({
    "user_message": message,
    "has_image": bool(image),
    "image_description": image_description
})

# Returns: intent (GENERAL_CONVERSATION | PRODUCT_RECOMMENDATION | IMAGE_SEARCH)
```

### 3. Search Engine Finds Products

```python
# search_engine.py
results = vector_store.search_similar_products(
    query=refined_query,
    top_k=9,                    # Get 9 candidates
    min_similarity=0.35         # Filter by 35% threshold
)
# Returns top 3 most relevant products
```

### 4. Vector Store Performs Similarity Search

```python
# vector_store.py
# Each product has 2-3 "views" indexed:
# - View A: Title + Features + Category
# - View B: Title + Description
# - View C: Search keywords

# Query embedding is compared against all views
# Best scoring view per product is kept
# Results filtered by min_similarity threshold
```

### 5. Frontend Displays Results

```typescript
// Products shown as cards below agent message
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
  {products.map(product => (
    <ProductCard key={product.id} product={product} />
  ))}
</div>
```

---

## 💻 Installation

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Pinecone** account ([Get API key](https://www.pinecone.io/))
- **Google Cloud** account with Gemini API access ([Get API key](https://aistudio.google.com/))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/AIAgent-comerceWebsite.git
cd AIAgent-comerceWebsite
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
EOF

# Process product data (creates data/processed_products.json)
python src/data_processor.py

# Setup vector store (indexes products in Pinecone)
python src/vector_store.py

# Start backend server
python api_server.py
# Server runs on http://localhost:5000
```

### 3. Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# App runs on http://localhost:5173
```

### 4. Open Browser

Navigate to `http://localhost:5173` and start chatting with Cartly!

---

## 🎮 Usage

### Text Search
```
You: "Find me wireless headphones under $50"
Cartly: "I found 3 products for you."
[Displays 3 relevant headphone products with images]
```

### Image Search
1. Click the **"+"** button in the input bar
2. Select **"Upload Image"**
3. Choose a product image (PNG/JPG, max 10MB)
4. Click **Send** or press Enter
5. Cartly analyzes the image and finds similar products

### Follow-up Questions
Click on suggested questions below agent responses to continue the conversation.

---

## 🔌 API Documentation

### `POST /api/chat`

Send a message to the AI agent.

**Request:**
```json
{
  "message": "Find wireless headphones",
  "image": "data:image/jpeg;base64,/9j/4AAQ..." // optional base64
}
```

**Response:**
```json
{
  "type": "product_search",
  "message": "I found 3 products for you.",
  "products": [
    {
      "id": "B08XYZ123",
      "title": "Sony Wireless Headphones WH-1000XM4",
      "category": "All Electronics",
      "price": 348.0,
      "rating": 4.7,
      "rating_count": 89234,
      "image_url": "https://...",
      "description": "Industry-leading noise canceling...",
      "similarity_score": 0.89
    }
  ],
  "follow_up_questions": [
    "Would you like to see more similar products?",
    "Are you looking for a specific price range?"
  ]
}
```

### `GET /api/agent-info`

Get agent metadata.

**Response:**
```json
{
  "name": "Cartly",
  "description": "AI Shopping Assistant",
  "total_products": 800,
  "available_categories": [
    "All Electronics",
    "AMAZON FASHION",
    "Sports & Outdoors",
    "..."
  ]
}
```

---

## ⚙️ Configuration

### Backend Environment Variables

```bash
# .env file
GEMINI_API_KEY=AIzaSy...          # Google Gemini API key
PINECONE_API_KEY=abc123...         # Pinecone API key
```

### Vector Store Settings

Edit `backend/src/vector_store.py`:

```python
class VectorStore:
    def __init__(self,
                 index_name: str = "amazon-products-test1",  # Pinecone index name
                 dimension: int = 384,                        # Embedding dimensions
                 metric: str = "cosine",                      # Similarity metric
                 upsert_batch_size: int = 100,               # Batch size for indexing
                 embed_batch_size: int = 64):                # Embedding batch size
```

### Search Quality Settings

Edit `backend/src/search_engine.py`:

```python
similar_products = self.vector_store.search_similar_products(
    refined_query,
    top_k=top_k * 3,              # Candidates to retrieve (e.g., 9 for top 3 results)
    min_similarity=0.35           # Minimum similarity threshold (0-1)
)
```

**Similarity Threshold Guide:**
- `0.9-1.0`: Nearly identical
- `0.7-0.9`: Very similar (same category + features)
- `0.5-0.7`: Moderately similar (related products)
- `0.35-0.5`: Somewhat related
- `< 0.35`: Filtered out (not relevant)

---

## 🎨 UI/UX Design

### Color Palette
```css
--bg-primary: #F2F2F2;    /* Light gray background */
--bg-accent: #EAE4D5;     /* Warm beige accents */
--border: #B6B09F;        /* Taupe borders */
--text: #000000;          /* Black text */
--white: #FFFFFF;         /* Pure white for cards */
```

### Design Principles
- **Minimalistic**: Clean, uncluttered interface
- **Conversation-first**: ChatGPT-like chat experience
- **Visual hierarchy**: Clear separation between messages and products
- **Responsive**: Mobile-first, works on all screen sizes
- **Accessible**: High contrast, clear typography

---

## 📊 Performance

- **Search latency**: < 500ms (vector search)
- **Image analysis**: 1-2 seconds (Gemini Vision)
- **Embedding generation**: < 100ms (local model)
- **Catalog size**: 800 products indexed
- **Vector dimensions**: 384 (optimized for speed)

---

## 🔒 Security

- ✅ API keys stored in environment variables
- ✅ CORS configured for frontend-backend communication
- ✅ Input validation on all endpoints
- ✅ File upload restrictions (10MB, PNG/JPG only)
- ✅ No sensitive data logged

---

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
vercel deploy
```

### Backend (Railway)
```bash
cd backend
# Add Procfile: web: python api_server.py
railway up
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) - AI capabilities
- [Pinecone](https://www.pinecone.io/) - Vector search infrastructure
- [BAML](https://www.boundaryml.com/) - LLM function management
- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [Amazon Product Data](https://cseweb.ucsd.edu/~jmcauley/datasets/amazon_v2/) - Product catalog

---

**Built with ❤️ using React, Python, and AI**