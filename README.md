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

### 💬 General Conversation

**Example Questions:**
```
"What's your name?"
"What can you do?"
"Which categories of products do you have?"
```

---

### 🔍 Text-Based Product Search

**Example Queries:**
```
"Find me wireless headphones under $50"
"Show me running shoes for women"
"I need a coffee maker"
"Recommend a laptop for students"
```

---

### 📸 Image-Based Product Search

**How to Use:**
1. Click the **"+"** button in the input bar
2. Select **"Upload Image"**
3. Choose a product image (PNG/JPG, max 10MB)
   - **Tip:** Download product images from catalog results and re-upload them to find similar products
4. Click **Send** to search

**Pro Tip:** Use clear product images with good lighting for best results.

---

## 🔌 API Endpoints

- `POST /api/chat` - Send chat message (text/image)
- `GET /api/agent/info` - Get agent capabilities and categories
- `GET /health` - Health check

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

## 🚀 Deployment

### Live Demo 🌐
- **Frontend**: [https://ai-agent-for-e-commerce.vercel.app](https://ai-agent-for-e-commerce.vercel.app)
- **Backend API**: [https://commerce-backend-edxgqpsgua-uc.a.run.app](https://commerce-backend-edxgqpsgua-uc.a.run.app)

---

### Backend Deployment (Google Cloud Run)

#### Prerequisites
- Google Cloud account with billing enabled
- gcloud CLI installed and authenticated
- Docker installed (for local testing)

#### Environment Variables Required
```bash
PINECONE_API_KEY=your_pinecone_api_key
GEMINI_API_KEY=your_gemini_api_key
HF_TOKEN=your_huggingface_token  # Optional but recommended to avoid rate limits
CORS_ORIGINS=*  # Or specify your frontend URL
```

#### Quick Deploy
```bash
# 1. Clone and navigate to project
git clone https://github.com/yourusername/AIAgent-comerceWebsite.git
cd AIAgent-comerceWebsite

# 2. Deploy using the deployment script
./deploy.sh

# The script will:
# - Build Docker image using Cloud Build (with layer caching for speed)
# - Push to Google Container Registry
# - Deploy to Cloud Run with optimized settings
# - Takes ~5-8 minutes first time, ~30-60 seconds for updates
```

#### Manual Deploy (Alternative)
```bash
# 1. Set your project ID
PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

# 2. Build and push Docker image
gcloud builds submit --config cloudbuild.yaml

# 3. Set environment variables in Cloud Run console or via CLI:
gcloud run services update commerce-backend \
  --region us-central1 \
  --update-env-vars PINECONE_API_KEY="your_key",GEMINI_API_KEY="your_key",HF_TOKEN="your_token"
```

#### Cloud Run Configuration
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Max Instances**: 10
- **Timeout**: 300 seconds
- **Region**: us-central1

#### View Logs
```bash
gcloud run services logs read commerce-backend --region us-central1 --limit 50
```

---

### Frontend Deployment (Vercel)

#### Prerequisites
- Vercel account (free tier works)
- GitHub repository connected to Vercel

#### Environment Variables Required
Create `.env.production` in `frontend/` directory:
```bash
VITE_API_BASE_URL=https://your-backend-url.run.app/api
```

#### Deploy via Vercel Dashboard
1. Connect your GitHub repository to Vercel
2. Set **Root Directory** to `frontend`
3. **Framework Preset**: Vite
4. **Build Command**: `npm run build`
5. **Output Directory**: `dist`
6. Add environment variable `VITE_API_BASE_URL`
7. Click **Deploy**

#### Deploy via CLI
```bash
cd frontend

# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Vercel will auto-detect Vite and deploy correctly
```

#### Auto-Deploy on Push
- Vercel automatically deploys on every `git push` to main branch
- Preview deployments created for pull requests
- Deployment typically takes 1-2 minutes

---

### Deployment Checklist ✅

**Before deploying:**
- [ ] All API keys added to Cloud Run environment variables
- [ ] Frontend `.env.production` points to correct backend URL
- [ ] `data/processed_products.json` exists and is committed to git
- [ ] Pinecone index created and populated with product vectors
- [ ] CORS configured to allow frontend domain

**After deploying:**
- [ ] Test `/health` endpoint: `curl https://your-backend.run.app/health`
- [ ] Test `/api/agent/info` endpoint to verify data loaded
- [ ] Test a chat message from frontend
- [ ] Verify images load correctly on frontend
- [ ] Check Cloud Run logs for any errors

---

### Troubleshooting

#### Backend Issues

**Problem**: `500 error on /api/agent/info`
```bash
# Solution: Ensure search engine is loaded
# Check logs: gcloud run services logs read commerce-backend --region us-central1
```

**Problem**: `HuggingFace rate limit error`
```bash
# Solution: Add HF_TOKEN environment variable
gcloud run services update commerce-backend \
  --region us-central1 \
  --update-env-vars HF_TOKEN="your_hf_token"
```

**Problem**: `Data file not found`
```bash
# Solution: Ensure data/processed_products.json is in git
git add -f data/processed_products.json
git commit -m "Add products data"
git push
```

#### Frontend Issues

**Problem**: JavaScript files returning HTML (MIME type error)
```bash
# Solution: Update vercel.json to use rewrites instead of routes
# Already fixed in latest version
```

**Problem**: API calls failing (CORS error)
```bash
# Solution: Verify VITE_API_BASE_URL in .env.production
# Ensure backend CORS_ORIGINS includes your frontend URL
```

**Problem**: Images not loading
```bash
# Solution: Ensure frontend/public/ is not in .gitignore
# Commit all assets in public folder
```

---

### Deployment Costs 💰

**Google Cloud Run (Backend)**
- Free tier: 2 million requests/month
- Typical usage: ~$5-20/month depending on traffic
- Scales to zero when not in use

**Vercel (Frontend)**
- Free tier: 100GB bandwidth/month
- Unlimited deployments
- Perfect for personal projects

**Pinecone (Vector Database)**
- Starter (free): 1 index, 100K vectors
- Sufficient for 800 products with multiple views

**Total**: Can run for **FREE** on free tiers! 🎉

---

## 🔮 Future Improvements

### Fine-Grained Attribute Matching
Currently, the RAG system retrieves semantically similar products but may not always capture highly specific attributes like exact colors, materials, or detailed specifications. For example:

- Query: "red t-shirt" → May return general t-shirts instead of only red ones
- Query: "leather jacket size XL" → May return leather jackets but not filter by size

**Planned Enhancements:**
1. **Attribute Extraction Layer**: Add NER (Named Entity Recognition) to extract specific attributes (color, size, brand, material) from user queries
2. **Hybrid Search**: Combine vector similarity with structured metadata filtering for precise attribute matching
3. **Query Expansion**: Automatically expand queries with synonyms and related terms (e.g., "crimson" → "red", "scarlet")
4. **Reranking with Attributes**: Implement attribute-aware reranking that prioritizes products matching specific constraints
5. **Improved Embeddings**: Fine-tune the embedding model on e-commerce product data to better capture product-specific semantics

These improvements will make the system more reliable for attribute-specific searches while maintaining its current strength in semantic understanding.

---

**Built with ❤️ using React, Python, and AI**