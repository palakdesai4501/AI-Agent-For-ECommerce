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

// Unified single-entrypoint helper types
class UserQueryInput {
  user_message string
  has_image bool
  image_description string?
}

class AgentDirective {
  intent ConversationType
  // For GENERAL_CONVERSATION
  reply string?
  // For PRODUCT_RECOMMENDATION or IMAGE_SEARCH
  refined_query string?
  user_filters string?
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


// (Removed unused AnalyzeSearchIntent)

// Single entrypoint: take one input and decide what to do.
function HandleUserQuery(input: UserQueryInput) -> AgentDirective {
  client Gemini
  prompt #"
    {{ ctx.output_format }}

    You are Cartly, an AI shopping assistant. Decide the user's intent and provide
    either a direct reply (for GENERAL_CONVERSATION) or a refined_query (for
    PRODUCT_RECOMMENDATION or IMAGE_SEARCH). Use the following rules:

    - If input.has_image is true, set intent = IMAGE_SEARCH. Use input.image_description
      to craft a concise refined_query for catalog search.
    - Otherwise, classify input.user_message as one of:
        GENERAL_CONVERSATION | PRODUCT_RECOMMENDATION
    - For GENERAL_CONVERSATION: set reply to a concise, helpful answer. Do not
      request tools.
    - For PRODUCT_RECOMMENDATION: create a refined_query that captures product type,
      key attributes, and any implicit constraints. Keep it short.

    STRICT AVAILABILITY / NO FABRICATION POLICY:
    - Never invent or imply availability of items that are not in the catalog.
    - Preserve hard constraints in the refined_query (e.g., color, brand, model, size, material).
    - Do not relax hard constraints unless the user explicitly permits alternatives.
    - If the query is "Recommend me red tshirt" and the catalog has no red t-shirts,
      keep the refined_query strict (e.g., "red t-shirt") so downstream search can return no results.
      The system should then clearly say no matching products were found rather than suggesting other colors.
    - When unsure between multiple interpretations, prefer the one that does not over-claim availability.

    Input:
    message: "{{ input.user_message }}"
    has_image: {{ input.has_image }}
    image_description: {{ input.image_description }}

  "#
}

// (Removed unused ToolSearchByText — handled by Python SearchEngine)

// TOOL 2: Context-aware product recommendations (RAG)
function GenerateProductRecommendations(
  user_query: string,
  retrieved_products: string
) -> string {
  client Gemini
  prompt #"
    {{ ctx.output_format }}

    You are Cartly, an AI shopping assistant. You have retrieved products from the catalog based on the user's query.
    Your task is to analyze the retrieved products and generate an accurate, helpful response.

    CRITICAL RULES:
    1. USE ONLY the information in the Retrieved Products context below
    2. Check if products match the user's specific requirements (color, size, material, brand, etc.)
    3. If NO products match the specific requirements:
       - Clearly state that you couldn't find exact matches
       - Explain what's missing (e.g., "I couldn't find red t-shirts")
       - Offer the retrieved products as alternatives with honest explanation
    4. If products DO match:
       - Highlight why each product is relevant
       - Mention key features, price, rating
    5. Never fabricate product details or availability
    6. Be honest and helpful

    User Query: "{{user_query}}"

    Retrieved Products:
    {{retrieved_products}}

    Generate a natural, conversational response that:
    - States whether exact matches were found
    - Explains relevance (or lack thereof) for each product
    - Provides honest recommendations or alternatives
    - Keeps response concise but informative
  "#
}

// TOOL 3: Single product explanation helper
function ExplainRecommendation(
  product: string,
  user_query: string
) -> string {
  client Gemini
  prompt #"
    Explain why this product is a good match for the user's search.
    USE ONLY the information present in Product. Do not assume brand, color,
    availability, or features that are not explicitly provided.
    If the product does not clearly satisfy key constraints in the User Query
    (e.g., color, size, model), state that directly and avoid claiming it does.

    User Query: "{{user_query}}"
    Product: {{product}}

    Provide a personalized explanation that highlights:
    1. How this product meets their specific needs
    2. Key features that make it stand out
    3. Value proposition

    Keep the explanation conversational and helpful, like a knowledgeable sales assistant.
    Be precise and do not fabricate details beyond the provided Product fields.
  "#
}