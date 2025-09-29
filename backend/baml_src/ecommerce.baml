enum ConversationType {
  GENERAL_CONVERSATION
  PRODUCT_RECOMMENDATION  
  IMAGE_SEARCH
}

class ProductRecommendation {
  product_id string
  title string
  description string
  category string
  price float?
  rating float?
  relevance_score float
  reason string
}

class SearchFilters {
  category string?
  min_price float?
  max_price float?
  min_rating float?
}

// ADD THESE NEW FUNCTIONS to your existing ecommerce.baml:

function ClassifyUserIntent(user_message: string, has_image: bool) -> ConversationType {
  client Gemini
  prompt #"
    Classify this user message into one of these categories:
    
    User message: "{{user_message}}"
    Has image attached: {{has_image}}
    
    Categories:
    - GENERAL_CONVERSATION: Greetings, questions about the agent capabilities, general chat
    - PRODUCT_RECOMMENDATION: Requests for product suggestions or search based on text
    - IMAGE_SEARCH: User wants to find products based on an uploaded image
    
    If has_image is true, return IMAGE_SEARCH.
    
    Return only the category name.
  "#
}

function HandleGeneralConversation(user_message: string) -> string {
  client Gemini
  prompt #"
    You are Cartly, a helpful AI shopping assistant for an e-commerce website.
    
    User message: "{{user_message}}"
    
    Respond in a friendly, helpful way. If asked about your capabilities, mention:
    - I can help you find products by describing what you need
    - I can search for products based on images you upload
    - I can have general conversations about shopping and products
    - I have access to 800 curated products from top e-commerce categories
    
    If asked about your name, say you're Cartly, the AI shopping assistant.
    Keep responses concise and engaging.
  "#
}

function AnalyzeProductImage(image_description: string) -> string {
  client Gemini
  prompt #"
    Based on this image description: "{{image_description}}"
    
    Generate a search query to find similar or related products in an e-commerce catalog.
    Focus on:
    - Product type and category
    - Key visual features (color, style, material)
    - Likely use case or purpose
    - Brand or style characteristics
    
    Return a concise search query that would find similar products.
  "#
}


function AnalyzeSearchIntent(query: string) -> string {
  client Gemini
  prompt #"
    Analyze the following search query and extract the user's intent:
    Query: "{{query}}"
    
    Determine:
    1. What type of product they're looking for
    2. Any implicit filters (price range, quality, etc.)
    3. The main search keywords to use
    
    Return a refined search query that captures the user's intent clearly.
    Keep it concise and focused on the main product attributes.
  "#
}

function GenerateProductRecommendations(
  query: string, 
  similar_products: string,
  user_filters: string?
) -> ProductRecommendation[] {
  client Gemini
  prompt #"
    Based on the user query: "{{query}}"
    
    Here are similar products found:
    {{similar_products}}
    
    {% if user_filters %}
    User preferences: {{user_filters}}
    {% endif %}
    
    Analyze these products and return the top 5 most relevant recommendations.
    For each product, provide:
    - A relevance_score (0-100)
    - A clear reason why this product matches the user's needs
    
    Focus on products that best match the user's intent, considering:
    - Product quality (rating)
    - Value for money
    - Feature alignment with user needs
    - Category relevance
    
    Return as JSON array.
  "#
}

function ExplainRecommendation(
  product: string,
  user_query: string
) -> string {
  client Gemini
  prompt #"
    Explain why this product is a good match for the user's search:
    
    User Query: "{{user_query}}"
    Product: {{product}}
    
    Provide a personalized explanation that highlights:
    1. How this product meets their specific needs
    2. Key features that make it stand out
    3. Value proposition
    
    Keep the explanation conversational and helpful, like a knowledgeable sales assistant.
  "#
}