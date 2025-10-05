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
  // Extracted filters from user query
  min_price float?
  max_price float?
  min_rating float?
  category string?
}

function HandleGeneralConversation(user_message: string) -> string {
  client Gemini
  prompt #"
    You are Cartly, a helpful AI shopping assistant for an e-commerce website.

    User message: "{{user_message}}"

    CATALOG CONTEXT:
    - 250 high-quality, curated products (all rated 3.5+ stars with 50+ reviews)
    - Main categories: Fashion (55), Health & Personal Care (35), Amazon Home (30), Pet Supplies (30), Office Products (21), Electronics (20), Sports & Outdoors (20), Computers (10), and more

    RESPONSE GUIDELINES:
    1. Be friendly, concise, and helpful (2-3 sentences max)
    2. If asked about capabilities, mention:
       - Text-based product search ("Find me wireless headphones")
       - Image-based search (upload a photo to find similar items)
       - Detailed product information and comparisons
    3. If asked about categories, mention the main ones listed above
    4. If asked about product availability, explain we have curated, high-quality products
    5. Never fabricate product details or availability

    Keep responses warm, professional, and action-oriented.
  "#
}

function AnalyzeProductImage(image_description: string) -> string {
  client Gemini
  prompt #"
    You are an e-commerce search expert. Convert this structured product description into a focused search query.

    Description:
    {{image_description}}

    TASK: Create a SHORT search query (4-8 words max) optimized for finding similar products.

    CRITICAL RULES:
    1. Start with the product type (REQUIRED - e.g., "shoes", "jacket", "headphones")
    2. Add target audience if clear (e.g., "women's", "men's", "kids")
    3. Add 1-2 key functional features (e.g., "athletic", "wireless", "insulated")
    4. SKIP specific colors, brands, and detailed materials (product catalogs often don't include these)
    5. Use BROAD, COMMON e-commerce terms that match typical product listings
    6. Keep queries GENERAL to maximize matches

    EXAMPLES:
    Input: "Product Type: Running Shoes, Colors: pink coral, Target: women, Features: athletic, mesh"
    Output: "women's athletic running shoes"
    ❌ BAD: "women's running shoes pink coral mesh" (too specific)

    Input: "Product Type: Jacket, Category: clothing, Colors: gray, Target: men, Features: hooded, waterproof"
    Output: "men's jacket hooded waterproof"
    ❌ BAD: "men's gray hooded waterproof jacket" (color too specific)

    Input: "Product Type: Headphones, Colors: black, Features: wireless, over-ear, bluetooth"
    Output: "wireless headphones over-ear"
    ❌ BAD: "black wireless over-ear bluetooth headphones" (redundant, too specific)

    Input: "Product Type: Water bottle, Features: insulated, stainless steel, Colors: blue"
    Output: "insulated water bottle stainless steel"
    ❌ BAD: "blue insulated stainless steel water bottle" (color unnecessary)

    Now generate the search query (favor BROAD terms over specific attributes):
  "#
}


// (Removed unused AnalyzeSearchIntent)

// Single entrypoint: take one input and decide what to do.
function HandleUserQuery(input: UserQueryInput) -> AgentDirective {
  client Gemini
  prompt #"
    {{ ctx.output_format }}

    You are Cartly, an AI shopping assistant with a curated catalog of 250 high-quality products.

    CATALOG OVERVIEW:
    - Fashion (clothing, shoes, jewelry): 55 products
    - Health & Personal Care: 35 products
    - Amazon Home (furniture, bedding, kitchen): 30 products
    - Pet Supplies: 30 products
    - Office Products: 21 products
    - Electronics: 20 products
    - Sports & Outdoors: 20 products
    - Computers: 10 products
    - Other categories (Tools, Beauty, Video Games, etc.): 29 products

    TASK: Classify user intent and generate appropriate response.

    CLASSIFICATION RULES:
    - If input.has_image is true → intent = IMAGE_SEARCH (use image_description to craft refined_query)
    - If user asks about agent capabilities, categories, or general questions → intent = GENERAL_CONVERSATION (provide helpful reply)
    - If user requests product recommendations or search → intent = PRODUCT_RECOMMENDATION (create refined_query)

    FOR GENERAL_CONVERSATION:
    - Provide a brief, helpful reply about Cartly's capabilities or catalog
    - Mention relevant categories if asked
    - Keep it friendly and concise (2-3 sentences)

    FOR PRODUCT_RECOMMENDATION:
    - Create a refined_query capturing: product type + key attributes (color, brand, style, etc.)
    - Keep it short and semantic (5-10 words)
    - Preserve specific constraints (e.g., "black comforter set", "wireless headphones", "women's running shoes")
    - DO NOT relax constraints - let search handle "not found" cases

    EXTRACT FILTERS (set to null if not mentioned):
    - min_price: If query mentions "under $X", "below $X", "less than $X" → set max_price = X
    - max_price: If query mentions "over $X", "above $X", "more than $X" → set min_price = X
    - min_price & max_price: If "between $X and $Y" → set both
    - min_rating: If mentions "highly rated", "top rated", "4+ stars" → set to 4.0 or 4.5
    - category: ALWAYS SET TO NULL (semantic search handles categories automatically)

    FILTER EXTRACTION EXAMPLES:
    - "recommend me products under $15" → refined_query: "products", max_price: 15.0
    - "find wireless headphones under $50" → refined_query: "wireless headphones", max_price: 50.0
    - "show me highly rated black comforter" → refined_query: "black comforter", min_rating: 4.0
    - "office products between $10 and $20" → refined_query: "office products", min_price: 10.0, max_price: 20.0, category: "Office Products"
    - "pet supplies over $30" → refined_query: "pet supplies", min_price: 30.0, category: "Pet Supplies"

    STRICT AVAILABILITY POLICY:
    - Never fabricate or imply product availability
    - Preserve ALL user constraints in refined_query AND extracted filters
    - If unsure, keep query specific - better to return no results than wrong results

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

    You are Cartly, an AI shopping assistant. You've retrieved products from a curated catalog of 250 high-quality items (all rated 3.5+ stars).

    User Query: "{{user_query}}"

    Retrieved Products:
    {{retrieved_products}}

    TASK: Generate a helpful, concise response (1-2 sentences).

    RESPONSE GUIDELINES:
    1. Count the EXACT number of products in the list
    2. If products found:
       - "I found [count] great option(s) for you!" (or similar friendly phrasing)
       - Optionally add brief context: "Here are [count] highly-rated [product type] that match your search."
       - If 3 products: mention "top 3 matches" or "best matches"
    3. If no products found:
       - "I couldn't find products matching '[query]' in our catalog."
       - Suggest trying broader terms or different categories
    4. DO NOT list product details (they're shown visually below)
    5. Keep it warm, helpful, and action-oriented

    EXAMPLES:
    - Found 3: "I found 3 great wireless headphones for you!"
    - Found 1: "I found 1 highly-rated comforter set that matches your search."
    - Found 0: "I couldn't find 'red wireless mouse' in our catalog. Try searching for 'wireless mouse' to see all available options."

    Generate response:
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