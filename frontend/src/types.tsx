export interface Product {
    id: string;
    title: string;
    description: string;
    category: string;
    price?: number;
    rating?: number;
    rating_count?: number;
    image_url?: string;
    product_url?: string;
    ai_relevance_score?: number;
    ai_recommendation_reason?: string;
    similarity_score?: number;
  }
  
  export interface Message {
    id: string;
    type: 'user' | 'agent';
    content: string;
    timestamp: Date;
    image?: string;
    products?: Product[];
    followUp?: string[];
    error?: boolean;
  }
  
  export interface AgentResponse {
    type: 'conversation' | 'product_search' | 'image_search' | 'error';
    message: string;
    products?: Product[];
    follow_up_questions?: string[];
    total_found?: number;
    agent_name?: string;
    image_description?: string;
    search_query?: string;
    error?: string;
  }
  
  export interface ChatRequest {
    message: string;
    image?: string;
    filters?: {
      category?: string;
      minPrice?: string;
      maxPrice?: string;
      minRating?: string;
    };
  }
  
  export interface AgentInfo {
    name: string;
    description: string;
    capabilities: string[];
    available_categories: string[];
    total_products: number;
  }