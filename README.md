# 🛒 Cartly - AI-Powered E-commerce Shopping Assistant

> An intelligent shopping assistant combining conversational AI, computer vision, and semantic search to help users discover products through natural language and image uploads.

![React](https://img.shields.io/badge/React-18-61DAFB?logo=react) ![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python) ![Gemini](https://img.shields.io/badge/Gemini-2.0-4285F4?logo=google) ![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-00D4AA)

**Live Demo**: [cartly-commerce-agent.vercel.app](https://cartly-commerce-agent.vercel.app)

---

## ✨ Features

🗣️ **Natural Conversation** - Chat with AI to find products using everyday language
🖼️ **Image Search** - Upload product photos to find similar items
🎯 **Smart Matching** - Semantic search with 0.25 similarity threshold filters irrelevant results
💬 **Clean UI** - ChatGPT-like interface with product cards

---

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Add API keys to .env
echo "GEMINI_API_KEY=your_key" > .env
echo "PINECONE_API_KEY=your_key" >> .env

# Setup data and vector store
python src/data_processor.py
python src/vector_store.py

# Start server
python api_server.py  # Runs on port 5000
```

### Frontend
```bash
cd frontend
npm install
npm run dev  # Runs on port 5173
```

Open `http://localhost:5173` and start chatting!

---

## 🏗️ How It Works

### Text Search
```
User Query → AI Intent Classification → Semantic Search (Pinecone) → Top 3 Products
```

### Image Search
```
Image Upload → Gemini Vision Analysis → Extract Attributes → Semantic Search → Results
```

**Key Components:**
- **Gemini 2.0 Flash Lite**: Vision analysis & conversation
- **BAML**: Type-safe LLM function calls
- **Pinecone**: Vector similarity search (384-dim embeddings)
- **all-MiniLM-L6-v2**: Lightweight embedding model

---

## 📁 Project Structure

```
backend/
├── src/
│   ├── conversational_agent.py   # Main AI agent logic
│   ├── search_engine.py          # Product search with vector DB
│   ├── vector_store.py           # Pinecone operations
│   └── data_processor.py         # Process raw product data
├── baml_src/ecommerce.baml       # LLM function definitions
├── data/processed_products.json  # 250 curated products
└── api_server.py                 # Flask API

frontend/
├── src/
│   ├── components/
│   │   ├── ChatInterface.tsx     # Main chat UI
│   │   └── ProductCard.tsx       # Product display cards
│   ├── services/api.ts           # API client
│   └── App.tsx
```

---

## 💬 Example Queries

**General Conversation:**
```
"What can you do?"
"What categories do you have?"
```

**Text Search:**
```
"wireless headphones under $50"
"running shoes for women"
"best coffee maker"
```

**Image Search:**
1. Click **"+"** button
2. Upload product image (PNG/JPG, max 10MB)
3. Agent finds visually similar products

---

## 🔌 API Endpoints

### `POST /api/chat`
```json
{
  "message": "Find wireless headphones",
  "image": "base64_string",  // optional
  "filters": {               // optional
    "min_price": 10,
    "max_price": 100
  }
}
```

**Response:**
```json
{
  "type": "product_search",
  "message": "I found 3 products for you.",
  "products": [...],
  "follow_up_questions": [...]
}
```

### `GET /api/agent/info`
Returns agent capabilities and catalog info (250 products, categories).

### `GET /health`
Health check for monitoring.

---

## ⚙️ Configuration

### Similarity Threshold
Edit `backend/src/search_engine.py:73`:
```python
min_similarity=0.25  # 0-1 scale (lower = more lenient)
```

**Threshold Guide:**
- `0.9-1.0`: Nearly identical
- `0.7-0.9`: Very similar
- `0.5-0.7`: Moderately similar
- `0.25-0.5`: Somewhat related
- `< 0.25`: Filtered out

### Environment Variables
```bash
# Backend (.env)
GEMINI_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
HF_TOKEN=your_hf_token  # Optional, prevents rate limits

# Frontend (.env.production)
VITE_API_BASE_URL=https://your-backend-url/api
```

---

## 🌐 Deployment

### Backend (Google Cloud Run)
```bash
./deploy.sh  # Automated deployment script
```

**Manual:**
```bash
gcloud builds submit --config cloudbuild.yaml
gcloud run services update commerce-backend \
  --update-env-vars GEMINI_API_KEY=key,PINECONE_API_KEY=key
```

**Settings:** 2GB memory, 2 vCPUs, 300s timeout

### Frontend (Vercel)
1. Connect GitHub repo to Vercel
2. Set **Root Directory**: `frontend`
3. Framework: Vite (auto-detected)
4. Add env var: `VITE_API_BASE_URL`
5. Deploy

**Auto-deploys** on every push to main.

---

## 🛠️ Tech Stack

**Frontend:** React 18, TypeScript, Vite, Tailwind CSS
**Backend:** Python, Flask, BAML
**AI:** Google Gemini 2.0 (vision + text), all-MiniLM-L6-v2 (embeddings)
**Database:** Pinecone (vector search)

---

## 🔮 Future Improvements

The current RAG system excels at semantic matching but may miss fine-grained attributes (exact colors, sizes, materials).

**Planned Enhancements:**
1. **NER Attribute Extraction** - Parse specific attributes from queries
2. **Hybrid Search** - Combine vector search with metadata filters
3. **Query Expansion** - Synonyms and related terms
4. **Attribute-Aware Reranking** - Prioritize exact attribute matches
5. **Fine-Tuned Embeddings** - E-commerce specific training

---

## 📊 Cost Estimate

- **Google Cloud Run**: Free tier → 2M requests/month (est. $5-20/month)
- **Vercel**: Free tier → 100GB bandwidth/month
- **Pinecone**: Free tier → 100K vectors (sufficient for 250 products)

**Total: Can run FREE on free tiers!** 🎉

---

**Built with ❤️ using React, Python, and AI**
